from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import viewsets
from rest_framework import status
from .models import Book ,Category
from .serializers import BookSerializer ,CategorySerializer
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import permission_classes
from django.core.mail import send_mail
from django.http import HttpResponse

# Create your views here.





@api_view(['GET'])
def GetAllBooks(request):
    books=Book.objects.all()
    serilaizers=BookSerializer(books, many=True).data
    return Response(serilaizers)

@api_view(['GET'])
def Getallcat(request):
        categories= Category.objects.all()
        serlizer =CategorySerializer(categories , many=True).data
        return Response(serlizer)



@api_view(['POST'])
@permission_classes([IsAuthenticated])
def AddBook(request):
    serializer=BookSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter]

    # فلترة بواسطة slug بدلاً من id
    filterset_fields = {
        'category__slug': ['exact'],  # فلترة باستخدام slug
        'title': ['icontains'],       # فلترة جزئية بواسطة العنوان
    }

    search_fields = ['title', 'category__name'] 
     # البحث باستخدام العنوان أو اسم الفئة


