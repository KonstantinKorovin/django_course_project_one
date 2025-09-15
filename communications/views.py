from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.cache import cache
from django.urls import reverse, reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)
from guardian.shortcuts import assign_perm

from communications.forms import MessageForm
from communications.models import Message
from mailings.models import SUCCESS, Mailing, MailingAttempt
from users.models import Recipient


class ListMailings(LoginRequiredMixin, ListView):
    model = Mailing
    template_name = "communications/home.html"
    context_object_name = "mailings"

    def get_queryset(self):
        return Mailing.objects.filter(owner=self.request.user)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        cache_key = f"mailings_context_{self.request.user.pk}"

        cached_stats = cache.get(cache_key)

        if cached_stats:
            context.update(cached_stats)
        else:
            user_mailings_queryset = self.get_queryset()
            successful_attempts = MailingAttempt.objects.filter(
                status=SUCCESS, mailing__in=user_mailings_queryset
            )
            successful_mailings_count = successful_attempts.values("mailing").distinct().count()

            if self.request.user.has_perm("mailings.can_view_all_mailings"):
                distinct_recipients = Recipient.objects.all().count()
            else:
                distinct_recipients = Recipient.objects.filter(owner=self.request.user).count()

            stats_context = {
                "successful_mailings_count": successful_mailings_count,
                "distinct_recipients": distinct_recipients,
            }

            cache.set(cache_key, stats_context, 60 * 15)
            context.update(stats_context)

        return context

class ListMessages(LoginRequiredMixin, ListView):
    model = Message
    template_name = "communications/list_messages.html"
    context_object_name = "messages"

    def get_queryset(self):
        cache_key = f"messages_{self.request.user.pk}"
        queryset = cache.get(cache_key)

        if queryset is None:
            queryset = Message.objects.filter(owner=self.request.user)
            queryset = list(queryset)

        cache.set(cache_key, queryset, 60 * 1)
        return queryset


class CreateMessage(LoginRequiredMixin, CreateView):
    model = Message
    form_class = MessageForm
    context_object_name = "message"
    template_name = "communications/create_message.html"
    success_url = reverse_lazy("communications:list-messages")

    def form_valid(self, form):
        form.instance.owner = self.request.user
        response = super().form_valid(form)

        assign_perm("communications.change_message", self.request.user, self.object)
        assign_perm("communications.view_message", self.request.user, self.object)
        assign_perm("communications.delete_message", self.request.user, self.object)

        cache.delete(f"messages_{self.request.user.pk}")
        return response


class UpdateMessage(LoginRequiredMixin, UpdateView):
    model = Message
    form_class = MessageForm
    template_name = "communications/create_message.html"

    def form_valid(self, form):
        response = super().form_valid(form)
        cache.delete(f"messages_{self.request.user.pk}")
        cache.delete(f"message_detail_{self.object.pk}")
        return response

    def get_queryset(self):
        queryset = super().get_queryset()

        if self.request.user.is_superuser:
            return queryset
        return queryset.filter(owner=self.request.user)

    def get_success_url(self):
        return reverse("communications:detail-message", args=[self.kwargs.get("pk")])


class DetailMessage(LoginRequiredMixin, DetailView):
    model = Message
    context_object_name = "message"
    template_name = "communications/detail_message.html"

    def get_object(self, queryset=None):
        pk = self.kwargs.get("pk")
        cache_key = f"message_detail_{pk}"
        message_object = cache.get(cache_key)
        if message_object:
            return message_object

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


class DeleteMessage(LoginRequiredMixin, DeleteView):
    model = Message
    success_url = reverse_lazy("communications:list-messages")
    template_name = "communications/delete_message.html"

    def post(self, request, *args, **kwargs):

        cache_key = f"messages_{self.request.user.pk}"
        response = super().post(request, *args, **kwargs)
        cache.delete(cache_key)
        return response

    def get_queryset(self):
        queryset = super().get_queryset()

        if self.request.user.is_superuser:
            return queryset
        return queryset.filter(owner=self.request.user)
