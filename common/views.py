# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.http import JsonResponse
from rest_framework.decorators import api_view

# Create your views here.

@api_view(['GET'])
def testAPI(params):
    response = {"Status": True}
    return JsonResponse(response, safe=False)
