import uuid

from config import celery_app
from django.core.mail import send_mail


@celery_app.task
def send_activation_mail(recipient: str, activation_link: uuid.UUID):
    send_mail(
        subject="User activation",
        message=f"Please, activate you account: {activation_link}",
        from_email="admin@support.com",
        recipient_list=[recipient],
    )


@celery_app.task
def send_confirmation_mail(recipient: str):
    send_mail(
        subject="Successful confirmation",
        message=f"You have successfully confirmed your email!",
        from_email="admin@support.com",
        recipient_list=[recipient],
    )
