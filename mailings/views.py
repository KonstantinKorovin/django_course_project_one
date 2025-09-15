from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.core.cache import cache
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
    View,
)
from guardian.shortcuts import assign_perm

from mailings.forms import MailingForm
from mailings.models import FINISHED, LAUNCHED, Mailing
from mailings.tasks import send_mailing_to_recipients


class MailingDisableView(PermissionRequiredMixin, View):
    permission_required = "mailings.can_disable_mailing"

    login_url = "users:user-login"

    def post(self, request, pk):
        mailing = get_object_or_404(Mailing, pk=pk)

        mailing.status = FINISHED
        mailing.save()
        return redirect(reverse("mailings:detail-mailing", kwargs={"pk": mailing.pk}))


class LaunchMailingView(LoginRequiredMixin, View):

    def post(self, request, pk):
        mailing = get_object_or_404(Mailing, pk=pk)

        mailing.status = LAUNCHED
        mailing.save()

        send_mailing_to_recipients(mailing.pk)
        return redirect(reverse("mailings:list-mailings"))


class ListMailings(LoginRequiredMixin, ListView):
    model = Mailing
    context_object_name = "mailings"
    template_name = "mailings/list_mailings.html"

    def get_queryset(self):
        user = self.request.user

        cache_key = f"mailings_{user.pk}"
        queryset = cache.get(cache_key)

        if queryset is None:
            if user.has_perm("mailings.can_view_all_mailings"):
                queryset = Mailing.objects.all()
            else:
                queryset = Mailing.objects.filter(owner=user)

            queryset = list(queryset)
            cache.set(cache_key, queryset, 60 * 1)
        return queryset


class CreateMailing(LoginRequiredMixin, CreateView):
    model = Mailing
    form_class = MailingForm
    context_object_name = "mailing"
    success_url = reverse_lazy("mailings:list-mailings")
    template_name = "mailings/create_mailing.html"

    def form_valid(self, form):
        form.instance.owner = self.request.user
        response = super().form_valid(form)
        assign_perm("mailings.change_mailing", self.request.user, self.object)
        assign_perm("mailings.view_mailing", self.request.user, self.object)
        assign_perm("mailings.delete_mailing", self.request.user, self.object)

        cache.delete(f"mailings_{self.request.user.pk}")
        return response

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs


class UpdateMailing(LoginRequiredMixin, UpdateView):
    model = Mailing
    template_name = "mailings/create_mailing.html"
    fields = ["first_date_mailing", "end_date_mailing", "message", "recipients"]

    def form_valid(self, form):
        response = super().form_valid(form)
        cache.delete(f"mailings_{self.request.user.pk}")
        cache.delete(f"mailing_detail_{self.object.pk}")
        return response

    def get_queryset(self):
        queryset = super().get_queryset()

        if self.request.user.is_superuser:
            return queryset
        return queryset.filter(owner=self.request.user)

    def get_success_url(self):
        return reverse("mailings:detail-mailing", args=[self.kwargs.get("pk")])


class DetailMailing(LoginRequiredMixin, DetailView):
    model = Mailing
    context_object_name = "mailing"
    template_name = "mailings/detail_mailing.html"

    def get_object(self, queryset=None):
        pk = self.kwargs.get("pk")
        cache_key = f"mailing_detail_{pk}"
        mailing_object = cache.get(cache_key)
        if mailing_object:
            return mailing_object

        self.object = super().get_object(queryset=queryset)
        cache.set(cache_key, self.object, timeout=60 * 15)
        return self.object

    def get_queryset(self):
        queryset = super().get_queryset()

        if (
            self.request.user.is_superuser
            or self.request.user.groups.filter(name="Managers").exists()
        ):
            return queryset
        return queryset.filter(owner=self.request.user)


class DeleteMailing(LoginRequiredMixin, DeleteView):
    model = Mailing
    success_url = reverse_lazy("mailings:list-mailings")
    template_name = "mailings/delete_mailing.html"

    def post(self, request, *args, **kwargs):
        cache_key = f"mailings_{self.request.user.pk}"
        response = super().post(request, *args, **kwargs)
        cache.delete(cache_key)
        return response

    def get_queryset(self):
        queryset = super().get_queryset()

        if self.request.user.is_superuser:
            return queryset
        return queryset.filter(owner=self.request.user)
