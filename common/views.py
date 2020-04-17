# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.http import JsonResponse
from rest_framework.decorators import api_view

# Create your views here.
from cluster.others.miscellaneous_operation import clean_instance_type_details


@api_view(['GET'])
def health_check(request):
    response = {"Status": True}
    return JsonResponse(response, safe=False)


@api_view(['GET'])
def alibaba_clear_instance_list(request):
    """
    Clear the alibaba instance list from database
    :param request:
    :return:
    """
    response = {"Status": True}
    clean_instance_type_details()
    return JsonResponse(response, safe=False)
