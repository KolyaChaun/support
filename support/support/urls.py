import json

import requests
from django.http import HttpRequest, JsonResponse
from django.urls import path


def get_current_market_state(request: HttpRequest) -> JsonResponse:
    if request.method == "POST":

        body_unicode = request.body.decode("utf-8")
        body = json.loads(body_unicode)
        from_currency = body["from_currency"]
        to_currency = body["to_currency"]

        url = f"https://www.alphavantage.co/query?function=CURRENCY_EXCHANGE_RATE&from_currency={from_currency}&to_currency={to_currency}&apikey=V2V43QAQ8RILGBOW"

        response = requests.get(url)
        result = response.json()
        rate = result["Realtime Currency Exchange Rate"]["5. Exchange Rate"]
        return JsonResponse({"rate": rate})


urlpatterns = [
    path(route="market", view=get_current_market_state),
]
