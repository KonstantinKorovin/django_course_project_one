from django import forms

from communications.models import Message


class MessageForm(forms.ModelForm):
    """Форма 'Сообщение'"""

    class Meta:
        model = Message
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super(MessageForm, self).__init__(*args, **kwargs)

        self.fields["theme"].widget.attrs.update(
            {"class": "form-control", "placeholder": "Введите тему сообщения"}
        )

        self.fields["message"].widget.attrs.update(
            {"class": "form-control", "placeholder": "Введите сообщение"}
        )
