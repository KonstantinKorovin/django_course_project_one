import secrets

from django.contrib.auth.forms import PasswordResetForm, SetPasswordForm
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.views import LoginView, LogoutView
from django.core.cache import cache
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.utils.decorators import method_decorator
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.views import View
from django.views.decorators.cache import cache_page
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)
from guardian.shortcuts import assign_perm

from config import settings
from config.settings import EMAIL_HOST_USER
from users.forms import CustomUserCreationForm, RecipientForm
from users.models import CustomUser, Recipient


class UserToggleActiveView(PermissionRequiredMixin, View):
    permission_required = "users.can_block_user"

    def post(self, request, pk):
        user = get_object_or_404(CustomUser, pk=pk)

        if user == self.request.user:
            return redirect(reverse("users:detail-user", kwargs={"pk": user.pk}))

        user.is_active = not user.is_active
        user.save()

        cache.delete(f"user_detail_{user.pk}")
        return redirect(reverse("users:detail-user", kwargs={"pk": user.pk}))


class ListUsers(ListView):
    model = CustomUser
    context_object_name = "users"
    template_name = "users/list_users.html"

    def get_queryset(self):
        user = self.request.user

        if user.has_perm("users.view_user"):
            return CustomUser.objects.all()
        return CustomUser.objects.filter(owner=user)


class DetailUser(DetailView):
    model = CustomUser
    context_object_name = "user"
    template_name = "users/detail_user.html"

    def get_object(self, queryset=None):
        pk = self.kwargs.get("pk")
        cache_key = f"user_detail_{pk}"
        user_object = cache.get(cache_key)
        if user_object:
            return user_object

        self.object = super().get_object(queryset=queryset)
        cache.set(cache_key, self.object, timeout=60 * 15)
        return self.object

    def get_queryset(self):
        user = self.request.user
        if user.has_perm("users.can_block_user") and user.has_perm("users.view_user"):
            return super().get_queryset()
        return CustomUser.objects.none()


class ListRecipients(LoginRequiredMixin, ListView):
    model = Recipient
    context_object_name = "recipients"
    template_name = "users/list_recipients.html"

    def get_queryset(self):
        user = self.request.user
        cache_key = f"users_{user.pk}"
        queryset = cache.get(cache_key)

        if queryset is None:
            if user.has_perm("users.can_view_all_recipients"):
                queryset = Recipient.objects.all()
            else:
                queryset = Recipient.objects.filter(owner=user)

            queryset = list(queryset)
            cache.set(cache_key, queryset, 60 * 15)
        return queryset


class CreateRecipient(LoginRequiredMixin, CreateView):
    model = Recipient
    form_class = RecipientForm
    context_object_name = "recipient"
    template_name = "users/create_recipient.html"
    success_url = reverse_lazy("users:list-recipients")

    def form_valid(self, form):
        form.instance.owner = self.request.user
        response = super().form_valid(form)

        assign_perm("users.view_recipient", self.request.user, self.object)
        assign_perm("users.change_recipient", self.request.user, self.object)
        assign_perm("users.delete_recipient", self.request.user, self.object)
        cache.delete(f"users_{self.request.user.pk}")
        return response


class UpdateRecipient(LoginRequiredMixin, UpdateView):
    model = Recipient
    form_class = RecipientForm
    template_name = "users/create_recipient.html"

    def form_valid(self, form):
        response = super().form_valid(form)
        cache.delete(f"users_{self.request.user.pk}")
        cache.delete(f"recipient_detail_{self.object.pk}")
        return response

    def get_queryset(self):
        queryset = super().get_queryset()

        if self.request.user.is_superuser:
            return queryset
        return queryset.filter(owner=self.request.user)

    def get_success_url(self):
        return reverse("users:detail-recipient", args=[self.kwargs.get("pk")])


class DetailRecipient(LoginRequiredMixin, DetailView):
    model = Recipient
    context_object_name = "recipient"
    template_name = "users/detail_recipient.html"

    def get_object(self, queryset=None):
        pk = self.kwargs.get("pk")
        cache_key = f"recipient_detail_{pk}"
        recipient_object = cache.get(cache_key)
        if recipient_object:
            return recipient_object

        self.object = super().get_object(queryset=queryset)
        cache.set(cache_key, self.object, timeout=60 * 15)
        return self.object

    def get_queryset(self):
        queryset = super().get_queryset()

        if (
            self.request.user.groups.filter(name="Managers").exists()
            or self.request.user.is_superuser
        ):
            return queryset
        return queryset.filter(owner=self.request.user)


class DeleteRecipient(LoginRequiredMixin, DeleteView):
    model = Recipient
    success_url = reverse_lazy("users:list-recipients")
    template_name = "users/delete_recipient.html"

    def post(self, request, *args, **kwargs):
        cache_key = f"users_{self.request.user.pk}"
        response = super().post(request, *args, **kwargs)
        cache.delete(cache_key)
        return response

    def get_queryset(self):
        queryset = super().get_queryset()

        if self.request.user.is_superuser:
            return queryset
        return queryset.filter(owner=self.request.user)


class LoginUserView(LoginView):
    template_name = "users/user_login.html"
    success_url = reverse_lazy("mailings:list-mailings")


class LogoutUserView(LogoutView):
    template_name = "users/user_logout.html"
    next_page = reverse_lazy("users:user-logout")


class RegisterUserView(CreateView):
    form_class = CustomUserCreationForm
    template_name = "users/user_register.html"
    success_url = reverse_lazy("mailings:list-mailings")

    def form_valid(self, form):
        """ """
        user = form.save()
        user.is_active = False
        token = secrets.token_hex(16)
        user.token = token
        user.save()
        host = self.request.get_host()
        url = f"http://{host}/users/email_confirm/{token}/"
        send_mail(
            subject="Подтверждение почты",
            message=f"Привет, перейди по ссылке для подтверждения почты {url}",
            from_email=EMAIL_HOST_USER,
            recipient_list=[user.email],
        )
        return super().form_valid(form)


def email_verification(request, token):
    """ """
    user = get_object_or_404(CustomUser, token=token)
    user.is_active = True
    user.save()
    return redirect(reverse("users:user-login"))


class PasswordResetView(View):
    template_name = "users/password_reset.html"

    def get(self, request, uidb64=None, token=None, *args, **kwargs):

        uidb64 = request.GET.get("uidb64", uidb64)
        token = request.GET.get("token", token)

        if uidb64 and token:
            try:
                uid = force_str(urlsafe_base64_decode(uidb64))
                user = CustomUser.objects.get(pk=uid)
            except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
                user = None

            if user and default_token_generator.check_token(user, token):
                form = SetPasswordForm(user=user)
                return render(
                    request,
                    self.template_name,
                    {
                        "form": form,
                        "uidb64": uidb64,
                        "token": token,
                        "is_password_set": True,
                    },
                )
            else:
                return render(
                    request,
                    self.template_name,
                    {
                        "message": "Ссылка недействительна или истекла.",
                        "status": "error",
                    },
                )
        else:
            form = PasswordResetForm()
            return render(
                request, self.template_name, {"form": form, "is_email_form": True}
            )

    def post(self, request, uidb64=None, token=None, *args, **kwargs):

        uidb64 = request.GET.get("uidb64", uidb64)
        token = request.GET.get("token", token)

        if uidb64 and token:
            try:
                uid = force_str(urlsafe_base64_decode(uidb64))
                user = CustomUser.objects.get(pk=uid)
            except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
                user = None

            form = SetPasswordForm(user=user, data=request.POST)
            if form.is_valid():
                form.save()
                return render(
                    request,
                    self.template_name,
                    {"message": "Ваш пароль успешно изменен.", "status": "success"},
                )
        else:
            form = PasswordResetForm(request.POST)
            if form.is_valid():
                email = form.cleaned_data["email"]
                try:
                    user = CustomUser.objects.get(email=email)
                    domain = request.get_host()
                    uid = urlsafe_base64_encode(force_bytes(user.pk))
                    token = default_token_generator.make_token(user)
                    reset_url = (
                        reverse("users:password-reset") + f"?uidb64={uid}&token={token}"
                    )
                    send_mail(
                        "Сброс пароля",
                        f"Для сброса пароля, перейдите по ссылке: http://{domain}{reset_url}",
                        settings.DEFAULT_FROM_EMAIL,
                        [user.email],
                        fail_silently=False,
                    )
                    return render(
                        request,
                        self.template_name,
                        {
                            "message": "Письмо для сброса пароля отправлено на ваш email.",
                            "status": "info",
                        },
                    )
                except CustomUser.DoesNotExist:
                    return render(
                        request,
                        self.template_name,
                        {
                            "message": "Пользователь с таким email не найден.",
                            "status": "error",
                        },
                    )
        return render(request, self.template_name, {"form": form})
