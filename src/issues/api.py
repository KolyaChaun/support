from rest_framework import generics, permissions, serializers, status
from rest_framework.response import Response

from issues.models import Issue
from users.enums import Role

from .enums import Status


class IsAdminOrSeniorUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.role in [Role.ADMIN, Role.SENIOR]


class IssueSerializer(serializers.ModelSerializer):
    status = serializers.IntegerField(required=False)
    junior = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Issue
        fields = "__all__"

    def validate(self, attrs):
        attrs["status"] = Status.OPENED
        return attrs


class IssuesAPI(generics.ListCreateAPIView):
    http_method_names = ["get", "post"]
    serializer_class = IssueSerializer

    def get_queryset(self):
        if self.request.user.role == Role.JUNIOR:
            return Issue.objects.filter(junior=self.request.user)
        elif self.request.user.role == Role.SENIOR:
            return Issue.objects.filter(senior=self.request.user)
        else:
            return Issue.objects.all()

    def post(self, request):
        if request.user.role == Role.SENIOR:
            raise Exception("The role is Senior")

        return super().post(request)


class IssuesRetrieveUpdateDeleteAPI(generics.RetrieveUpdateDestroyAPIView):
    http_method_names = ["get", "put", "delete"]
    serializer_class = IssueSerializer
    queryset = Issue.objects.all()
    lookup_url_kwarg = "id"

    def get_permissions(self):
        if self.request.method == "PUT":
            return [IsAdminOrSeniorUser()]
        elif self.request.method in "DELETE":
            return [permissions.IsAdminUser()]
        else:
            return [permissions.IsAuthenticated()]

    def destroy(self, request, *args, **kwargs):
        if not request.user.is_staff:
            return Response(status=status.HTTP_403_FORBIDDEN)
        return super().destroy(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        if self.request.user == Role.JUNIOR:
            return Response(status=status.HTTP_403_FORBIDDEN)
        return super().update(request, *args, **kwargs)
