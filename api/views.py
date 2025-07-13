from rest_framework import generics
from .models import Book
from .serializers import BookSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

class BookListCreateAPIView(generics.ListCreateAPIView):
    queryset = Book.objects.all()
    serializer_class = BookSerializer

class AnalizeView(APIView):
    def post(self, request):
        data = request.data  # 获取 POST 请求体，通常为 JSON
        # 示例处理：你可以替换为实际分析逻辑
        result = {"received": data}
        return Response(result, status=status.HTTP_200_OK)