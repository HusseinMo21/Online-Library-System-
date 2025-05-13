from rest_framework import serializers
from .models import Book
from .models import Category


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']        
        read_only_fields = ['slug']
class BookSerializer(serializers.ModelSerializer):
  
    category = serializers.StringRelatedField() 
    added_by = serializers.StringRelatedField()  
    class Meta:
        model = Book
        fields = '__all__'

