from rest_framework import serializers
from .models import User
from api.models import Book  # تأكد من أن لديك الاستيراد الصحيح

class UserSerializer(serializers.ModelSerializer):
    favorite_books = serializers.PrimaryKeyRelatedField(queryset=Book.objects.all(), many=True, required=False)

    class Meta:
        model = User
        fields = ['email', 'name', 'password', 'favorite_books']
        extra_kwargs = {
            'password': {'write_only': True}  # علشان كلمة السر ما تتعرضش في الاستجابة
        }

    def create(self, validated_data):
        favorite_books_data = validated_data.pop('favorite_books', [])
        password = validated_data.pop('password', None)
        
        # إنشاء المستخدم بدون favorite_books أولاً
        user = User.objects.create(**validated_data)
        
        if password:
            user.set_password(password)
            user.save()
        
        # إضافة الكتب المفضلة
        for book in favorite_books_data:
            user.favorite_books.add(book)
        
        return user
