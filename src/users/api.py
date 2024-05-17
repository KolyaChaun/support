import redis
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from rest_framework import generics, permissions, serializers, status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView
from users.enums import Role
from users.tasks import send_confirmation_mail

from .services import Activator

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = "__all__"


class UserCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["email", "password", "first_name", "last_name", "role"]

    def validate(self, attrs: dict) -> dict:
        attrs["password"] = make_password(attrs["password"])
        return attrs

    def validate_role(self, value: str) -> str:
        if value not in Role.users():
            raise ValidationError(
                f"Selected Role must be in {Role.users_values()}",
            )
        return value


class UserCreatePublicSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["email", "first_name", "last_name", "role"]


class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "first_name", "last_name"]

    def update(self, instance, validated_data):
        instance.first_name = validated_data.get(
            "first_name", instance.first_name
        )
        instance.last_name = validated_data.get(
            "last_name", instance.last_name
        )
        instance.save()
        return instance


class UserCreateAPI(generics.CreateAPIView):
    http_method_names = ["post"]
    serializer_class = UserCreateSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        return User.objects.all()

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        activator_service = Activator(email=serializer.data["email"])
        activation_key = activator_service.create_activation_key()
        activator_service.save_activation_information(
            internal_user_id=serializer.instance.id,
            activation_key=activation_key,
        )
        activator_service.send_user_activation_email(
            activation_key=activation_key
        )

        return Response(
            UserCreatePublicSerializer(serializer.validated_data).data,
            status=status.HTTP_201_CREATED,
            headers=self.get_success_headers(serializer.data),
        )


class UserRetrieveUpdateAPI(generics.RetrieveUpdateDestroyAPIView):
    http_method_names = ["get", "put"]
    serializer_class = UserUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_url_kwarg = "id"

    def get_queryset(self):
        return User.objects.all()

    def get_serializer_class(self):
        if self.request.method == "GET":
            return UserSerializer
        if self.request.method == "PUT":
            return UserUpdateSerializer


class UserDestroyAPI(generics.DestroyAPIView):
    http_method_names = ["delete"]
    permission_classes = [permissions.IsAdminUser]
    lookup_url_kwarg = "id"

    def get_queryset(self):
        return User.objects.all()

    def destroy(self, request, *args, **kwargs):
        if not request.user.is_staff:
            return Response(status=status.HTTP_403_FORBIDDEN)

        return super().destroy(request, *args, **kwargs)


class UserActivateAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        activator_service = Activator()
        activation_key = request.data.get("activation_key")

        validate_data = activator_service.validate_activation(activation_key)
        if "error" in validate_data:
            return Response(validate_data, status=status.HTTP_404_NOT_FOUND)
        else:
            internal_user_id = validate_data["user_id"]
            user = User.objects.get(id=internal_user_id)
            email = user.email
            user.is_active = True
            user.save()

            connection_redis = redis.Redis.from_url(settings.CACHE_URL)
            connection_redis.delete(f"activation:{activation_key}")

            send_confirmation_mail.delay(email)
            return Response(
                {"message": "User activated successfully"},
                status=status.HTTP_200_OK,
            )
