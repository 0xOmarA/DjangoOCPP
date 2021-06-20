from django.shortcuts import render
from django.http import JsonResponse

from ocpp_lib.call import Call
from ocpp_lib.types import RemoteStartTransaction_Req, IdToken

async def test_view(request):
    return JsonResponse({'yes': 'yes'})