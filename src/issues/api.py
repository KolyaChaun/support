from rest_framework import generics, serializers, status
from rest_framework.response import Response

from issues.models import Issue
from users.enums import Role

from .enums import Status


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

    def destroy(self, request, *args, **kwargs):
        if self.request.user.role == Role.ADMIN:
            instance = self.get_object()
            self.perform_destroy(instance)
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(
                status=status.HTTP_403_FORBIDDEN, data={"Only admin can delete issues"}
            )

    def update(self, request, *args, **kwargs):
        if (
            self.request.user.role == Role.ADMIN
            or self.request.user.role == Role.SENIOR
        ):
            partial = kwargs.pop("partial", False)
            instance = self.get_object()
            serializer = self.get_serializer(
                instance, data=request.data, partial=partial
            )
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(
                status=status.HTTP_403_FORBIDDEN,
                data={"Only admin and senior can update issues"},
            )
