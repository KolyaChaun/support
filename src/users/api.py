from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from rest_framework import generics, permissions, serializers, status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from users.enums import Role

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
        instance.first_name = validated_data.get("first_name", instance.first_name)
        instance.last_name = validated_data.get("last_name", instance.last_name)
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

        return Response(
            UserCreatePublicSerializer(serializer.validated_data).data,
            status=status.HTTP_201_CREATED,
            headers=self.get_success_headers(serializer.data),
        )


class UserUpdateAPI(generics.RetrieveUpdateDestroyAPIView):
    http_method_names = ["get", "put", "delete"]
    serializer_class = UserUpdateSerializer
    permission_classes = [permissions.AllowAny]
    lookup_url_kwarg = "id"

    def get_queryset(self):
        return User.objects.all()

    def get_serializer_class(self):
        if self.request.method == "GET":
            return UserSerializer
        if self.request.method == "PUT":
            return UserUpdateSerializer

    def destroy(self, request, *args, **kwargs):
        if self.request.user.role == Role.ADMIN:
            instance = self.get_object()
            self.perform_destroy(instance)
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(
                status=status.HTTP_403_FORBIDDEN, data={"Only admin can delete user"}
            )
