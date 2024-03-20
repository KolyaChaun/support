import json

from django.http import HttpRequest, JsonResponse

from issues.models import Issue


def create_new_issue(request: HttpRequest) -> JsonResponse:
    if request.method != "POST":
        raise Exception("Only POST method for function 'create_new_issue' ")

    data = json.loads(request.body)
    issue = Issue.objects.create(
        junior_id=data.get("junior_id"),
        senior_id=data.get("senior_id"),
        title=data.get("title"),
        body=data.get("body"),
    )
    result = {
        "id": issue.id,
        "title": issue.title,
        "body": issue.body,
        "senior_id": issue.senior_id,
        "junior_id": issue.junior_id,
    }
    return JsonResponse(data=result)


def get_issue(request: HttpRequest) -> JsonResponse:
    if request.method != "GET":
        raise Exception("Only GET method for function 'get_issue' ")

    issues: list[Issue] = Issue.objects.all()

    results: list[dict] = [
        {
            "id": issue.id,
            "title": issue.title,
            "body": issue.body,
            "senior_id": issue.senior_id,
            "junior_id": issue.junior_id,
        }
        for issue in issues
    ]
    return JsonResponse(data={"results": results})
