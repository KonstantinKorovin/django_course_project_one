from django import forms

from communications.models import Message

from .models import Mailing, MailingAttempt, Recipient


class MailingForm(forms.ModelForm):
    message = forms.ModelChoiceField(queryset=Message.objects.none(), label="Сообщение")
    recipients = forms.ModelMultipleChoiceField(
        queryset=Recipient.objects.none(),
        widget=forms.CheckboxSelectMultiple,
        label="Получатели",
    )

    class Meta:
        model = Mailing
        fields = ["first_date_mailing", "end_date_mailing", "message", "recipients"]

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        if user:
            self.fields["message"].queryset = Message.objects.filter(owner=user)
            self.fields["recipients"].queryset = Recipient.objects.filter(owner=user)

            if self.instance and self.instance.pk:
                if self.instance.message:
                    self.fields["message"].queryset |= Message.objects.filter(
                        pk=self.instance.message.pk
                    )

                self.fields["recipients"].queryset |= self.instance.recipients.all()


class MailingAttemptForm(forms.ModelForm):
    """Форма 'Попытка рассылки'"""

    class Meta:
        model = MailingAttempt
        fields = "__all__"
