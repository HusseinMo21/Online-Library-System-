from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from .serializers import UserSerializer
from api.models import Book
from api.serializers import BookSerializer
from datetime import timedelta
from .models import User
from django.conf import settings
from api.utils.email import send_email
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from django.shortcuts import get_object_or_404
from django.utils.encoding import force_bytes
# Register endpoint
@api_view(['POST'])
def register(request):
    email = request.data.get('email')
    User = get_user_model()

    if User.objects.filter(email=email).exists():
        return Response({'error': 'Email already exists'}, status=status.HTTP_400_BAD_REQUEST)

    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()

        user.is_active = False  # المستخدم غير مفعل لحد ما يأكد الإيميل
        user.save()

        # توليد الرابط
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        verification_link = f"{settings.FRONTEND_URL}/verify-email/{uid}/{token}/"

        # رسالة التحقق HTML لطيفة
        subject = 'تأكيد بريدك الإلكتروني'
        html = f"""
            <div style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <h2>مرحبًا بك في موقعنا!</h2>
                <p>شكرًا لتسجيلك. من فضلك قم بتأكيد بريدك الإلكتروني من خلال الضغط على الزر أدناه:</p>
                <p style="text-align: center;">
                    <a href="{verification_link}" style="
                        background-color: #4CAF50;
                        color: white;
                        padding: 12px 20px;
                        text-decoration: none;
                        border-radius: 5px;
                        display: inline-block;
                        font-weight: bold;
                    ">
                        تأكيد البريد الإلكتروني
                    </a>
                </p>
                <p>إذا لم يعمل الزر، يمكنك نسخ هذا الرابط وفتحه في المتصفح:</p>
                <p><a href="{verification_link}">{verification_link}</a></p>
                <br>
                <p>تحياتنا،<br>فريق الدعم</p>
            </div>
        """

        # إرسال الإيميل
        send_email(
            to_email=user.email,
            subject=subject,
            html=html
        )

        return Response({
            'message': 'تم إنشاء الحساب. تحقق من بريدك الإلكتروني لتأكيد الحساب.',
            'user': serializer.data,
        }, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
# Login endpoint
@api_view(['POST'])
def login(request):
    email = request.data.get('email')
    password = request.data.get('password')

    User = get_user_model()
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_401_UNAUTHORIZED)

    if not user.check_password(password):
        return Response({'error': 'Invalid password'}, status=status.HTTP_401_UNAUTHORIZED)

    if not user.is_email_verified:
        return Response({'error': 'Email not verified. Please verify your email first.'}, status=status.HTTP_403_FORBIDDEN)

    refresh = RefreshToken.for_user(user)
    access_token = refresh.access_token
    access_token.set_exp(lifetime=timedelta(hours=1))
    refresh.set_exp(lifetime=timedelta(days=7))

    serializer = UserSerializer(user)

    return Response({
        'refresh': str(refresh),
        'access': str(access_token),
        'user': serializer.data,
    }, status=status.HTTP_200_OK)

# Get user profile endpoint
@api_view(['GET'])
@permission_classes([IsAuthenticated])  
def get_user_profile(request):
    user = request.user  # الحصول على اليوزر الحالي من التوكن
    serializer = UserSerializer(user)
    return Response(serializer.data)

# Get user's books endpoint
@api_view(['GET'])
@permission_classes([IsAuthenticated])  
def user_books(request):
    books = Book.objects.filter(added_by=request.user)
    serializer = BookSerializer(books, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

# Refresh access token endpoint
@api_view(['POST'])
def refresh_access_token(request):
    refresh_token = request.data.get('refresh')

    try:
        refresh = RefreshToken(refresh_token)
        access_token = refresh.access_token
        access_token.set_exp(lifetime=timedelta(hours=1))  # مدة صلاحية ساعة جديدة

        return Response({
            'access': str(access_token),
        }, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({'error': 'Invalid refresh token or expired'}, status=status.HTTP_401_UNAUTHORIZED)



@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_user_profile(request):
    user = request.user
    serializer = UserSerializer(user, data=request.data, partial=True)
    
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



@api_view(['POST'])
def password_reset(request):
    email = request.data.get('email')
    User = get_user_model()

    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return Response({'error': 'Email not found'}, status=status.HTTP_400_BAD_REQUEST)

    # توليد توكن استعادة كلمة المرور
    token = default_token_generator.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))

    # رابط استعادة كلمة المرور
    reset_link = f"{settings.FRONTEND_URL}/reset-password/{uid}/{token}/"

    # إرسال البريد الإلكتروني
    subject = 'Reset your password'
    message = f'Click the link below to reset your password: \n{reset_link}'

    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email], fail_silently=False)

    return Response({'message': 'Check your email for the reset link.'}, status=status.HTTP_200_OK)

@api_view(['POST'])
def verify_email(request):
    uid = request.data.get('uid')
    token = request.data.get('token')

    try:
        uid = urlsafe_base64_decode(uid).decode()
        user = get_object_or_404(get_user_model(), pk=uid)

        if default_token_generator.check_token(user, token):
            user.is_active = True
            user.is_email_verified = True 
            user.save()

            return Response({'message': 'Email successfully verified!'}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Invalid token or token expired.'}, status=status.HTTP_400_BAD_REQUEST)
    except Exception:
        return Response({'error': 'Invalid UID or token.'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def set_new_password(request):
    uid = request.data.get('uid')
    token = request.data.get('token')
    new_password = request.data.get('password')

    try:
        uid = urlsafe_base64_decode(uid).decode()
        user = get_user_model().objects.get(pk=uid)

        if default_token_generator.check_token(user, token):
            user.set_password(new_password)
            user.save()
            return Response({'message': 'Password has been reset.'}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Invalid or expired token.'}, status=status.HTTP_400_BAD_REQUEST)
    except Exception:
        return Response({'error': 'Something went wrong.'}, status=status.HTTP_400_BAD_REQUEST)





@api_view(['POST'])
def add_to_favorites(request):
    """إضافة كتاب إلى المفضلة"""
    if not request.user.is_authenticated:
        return Response({"detail": "Authentication credentials were not provided."}, status=status.HTTP_401_UNAUTHORIZED)

    book_id = request.data.get("book_id")
    try:
        book = Book.objects.get(id=book_id)
    except Book.DoesNotExist:
        return Response({"detail": "Book not found."}, status=status.HTTP_404_NOT_FOUND)

    user = request.user
    user.favorite_books.add(book)  # إضافة الكتاب إلى مفضلة المستخدم
    return Response({"detail": "Book added to favorites."}, status=status.HTTP_200_OK)

@api_view(['POST'])
def remove_from_favorites(request):
    """حذف كتاب من المفضلة"""
    if not request.user.is_authenticated:
        return Response({"detail": "Authentication credentials were not provided."}, status=status.HTTP_401_UNAUTHORIZED)

    book_id = request.data.get("book_id")
    try:
        book = Book.objects.get(id=book_id)
    except Book.DoesNotExist:
        return Response({"detail": "Book not found."}, status=status.HTTP_404_NOT_FOUND)

    user = request.user
    user.favorite_books.remove(book)  # إزالة الكتاب من مفضلة المستخدم
    return Response({"detail": "Book removed from favorites."}, status=status.HTTP_200_OK)

@api_view(['GET'])
def get_favorite_books(request):
    """عرض كل الكتب المفضلة للمستخدم"""
    if not request.user.is_authenticated:
        return Response({"detail": "Authentication credentials were not provided."}, status=status.HTTP_401_UNAUTHORIZED)

    user = request.user
    favorite_books = user.favorite_books.all()  # استرجاع جميع الكتب المفضلة للمستخدم
    serializer = BookSerializer(favorite_books, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)