from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AddBook, Getallcat, BookViewSet


router = DefaultRouter()
router.register('books', BookViewSet, basename='book')

urlpatterns = [
    path('allcateigories/', Getallcat, name='Getallcat'),
    path('books/create/', AddBook, name='AddBook'),
    path('', include(router.urls)),  
]