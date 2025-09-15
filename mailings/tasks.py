from django.conf import settings
from django.core.mail import send_mail

from mailings.models import LAUNCHED, NOT_SUCCESS, SUCCESS, Mailing, MailingAttempt


def send_mailing_to_recipients(mailing_pk):
    """Функция для отправки рассылки пользователю"""
    mailing = Mailing.objects.get(pk=mailing_pk)
    recipient_list = list(mailing.recipients.values_list("email", flat=True))

    mailing_instance = None

    if not recipient_list:
        print(f"Рассылка с ID {mailing_pk} не имеет получателей. Отправка отменена.")
        MailingAttempt.objects.create(
            mailing=mailing_instance,
            status=NOT_SUCCESS,
            response_status="Отправка невозможна: нет получаетелей.",
        )
        return

    subject = mailing.message.theme
    message_body = mailing.message.message
    status = SUCCESS
    response_status = f"Рассылка успешно отправлена {len(recipient_list)} получателям."

    send_mail(
        subject=subject,
        message=message_body,
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=recipient_list,
        fail_silently=False,
    )

    print(response_status)
    mailing.status = LAUNCHED
    mailing.save()

    MailingAttempt.objects.create(
        mailing=mailing, status=status, response_status=response_status
    )
