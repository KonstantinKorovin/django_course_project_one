from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from users.models import CustomUser, Recipient


class RecipientForm(forms.ModelForm):
    """Форма 'Получатель'"""

    class Meta:
        model = Recipient
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super(RecipientForm, self).__init__(*args, **kwargs)

        self.fields["email"].widget.attrs.update(
            {"class": "form-control", "placeholder": "Введите почту"}
        )

        self.fields["full_name"].widget.attrs.update(
            {"class": "form-control", "placeholder": "Введите полное имя"}
        )

        self.fields["comment"].widget.attrs.update(
            {"class": "form-control", "placeholder": "Укажите комментарий"}
        )


class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = [
            "username",
            "email",
        ]


class CustomUserAuthenticationForm(AuthenticationForm):
    pass
