from django.db.models import Q
from django.shortcuts import get_object_or_404
from issues.models import Issue, Message
from rest_framework import generics, permissions, response, serializers, status
from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response
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


class IssueStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Issue
        fields = ["id", "title", "status"]


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


class MessageSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    issue = serializers.PrimaryKeyRelatedField(queryset=Issue.objects.all())

    class Meta:
        model = Message
        fields = "__all__"

    def save(self):
        if (user := self.validated_data.pop("user", None)) is not None:
            self.validated_data["user_id"] = user.id

        if (issue := self.validated_data.pop("issue", None)) is not None:
            self.validated_data["issue_id"] = issue.id

        return super().save()


@api_view(["GET", "POST"])
def messages_api_dispatcher(request: Request, issue_id: int):
    if request.method == "GET":
        messages = Message.objects.filter(
            Q(
                issue__id=issue_id,
                issue__junior=request.user,
            )
            | Q(
                issue__id=issue_id,
                issue__senior=request.user,
            )
        ).order_by("-timestamp")
        serializer = MessageSerializer(messages, many=True)

        return response.Response(serializer.data)
    else:
        issue = Issue.objects.get(id=issue_id)
        payload = request.data | {"issue": issue.id}
        serializer = MessageSerializer(
            data=payload, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return response.Response(serializer.validated_data)


@api_view(["PUT"])
def issues_close(request: Request, id: int):
    issue = get_object_or_404(Issue, id=id)

    if request.user.role != Role.SENIOR:
        raise PermissionError("Only senior users can close issues")

    if issue.status != Status.IN_PROGRESS:
        return response.Response(
            {"message": "Issue is not IN_POGRESS"},
            status=422,
        )
    else:
        issue.status = Status.CLOSED
        issue.save()

    serializer = IssueStatusSerializer(issue)

    return response.Response(serializer.data)


@api_view(["PUT"])
def issues_take(request: Request, id: int):
    issue = get_object_or_404(Issue, id=id)

    if request.user.role != Role.SENIOR:
        raise PermissionError("Only senior users can take issues")

    if (issue.status != Status.OPENED) or (issue.senior is not None):
        return response.Response(
            {"message": "Issue is not Opened or senior is set..."},
            status=422,
        )
    else:
        issue.senior = request.user
        issue.status = Status.IN_PROGRESS
        issue.save()

    serializer = IssueStatusSerializer(issue)

    return response.Response(serializer.data)
