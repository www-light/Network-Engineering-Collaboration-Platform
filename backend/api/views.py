from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status


@api_view(['GET'])
def health_check(request):
    """健康检查接口"""
    return Response({
        'status': 'success',
        'message': 'Django后端服务运行正常'
    }, status=status.HTTP_200_OK)

