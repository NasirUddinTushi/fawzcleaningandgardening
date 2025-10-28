from django.http import JsonResponse
from .models import QuoteRequest

def get_quote_request(request, pk):
    try:
        qr = QuoteRequest.objects.get(pk=pk)
        return JsonResponse({
            "city": qr.city or "",
            "postal_code": qr.postal_code or "",
            "address": qr.address or "",
        })
    except QuoteRequest.DoesNotExist:
        return JsonResponse({
            "city": "",
            "postal_code": "",
            "address": ""
        }, status=404)
