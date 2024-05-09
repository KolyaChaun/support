import uuid

from django.shortcuts import get_object_or_404

from .models import ActivationKey, User
from .tasks import send_activation_mail


class Activator:
    def __init__(self, email: str):
        self.email = email

    def create_activation_key(self) -> uuid.UUID:
        return uuid.uuid3(namespace=uuid.uuid4(), name=self.email)

    def create_activation_link(self, activation_key: uuid.UUID) -> str:
        return f"https://frontend.com/users/activate/{activation_key}"

    def send_user_activation_email(self, activation_key: uuid.UUID) -> None:
        """Send activation email using SMTP."""

        activation_link = self.create_activation_link(activation_key)

        send_activation_mail.delay(
            recipient=self.email,
            activation_link=activation_link,
        )

    def save_activation_information(
        self, internal_user_id: int, activation_key: uuid.UUID
    ) -> None:
        user = get_object_or_404(User, id=internal_user_id)
        activation_key = ActivationKey(
            user=user, activation_key=activation_key
        )
        activation_key.save()

    def validate_activation(self, activation_key: uuid.UUID) -> None:
        activation_keys = ActivationKey.objects.filter(key=activation_key)
        if activation_keys.exists():
            activation_key_instance = activation_keys.first()
            user = activation_key_instance.user
            user.is_active = True
            user.save()
            return user
        return None
