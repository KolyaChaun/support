import json
import uuid

import redis
from django.conf import settings

from .tasks import send_activation_mail


class Activator:
    def __init__(self, email: str = None):
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
        connection_redis = redis.Redis.from_url(settings.CACHE_URL)
        payload = {"user_id": internal_user_id}
        connection_redis.set(
            f"activation:{activation_key}", json.dumps(payload), ex=200
        )

    def validate_activation(self, activation_key: uuid.UUID):
        connection_redis = redis.Redis.from_url(settings.CACHE_URL)
        cache_data = connection_redis.get(f"activation:{activation_key}")
        if not cache_data:
            return {"error": "Invalid or expired activation key."}

        payload = json.loads(cache_data)
        return payload
