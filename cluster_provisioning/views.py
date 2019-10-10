from django.http import JsonResponse
from rest_framework.decorators import api_view



@api_view(['GET'])
def all_cluster_details(request):
    """
    get the details of all clusters
    :param request:
    :return:
    """
    api_response = {}
    access_flag = True
    try:
        pass
    except Exception as e:
        pass
    finally:
        return JsonResponse({"done": "successfully"}, safe=False)
