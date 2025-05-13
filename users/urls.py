from . import views
from django.urls import path , include



urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('profile/', views.get_user_profile, name='user-profile'),
    path('my-books/', views.user_books, name='user-books'),
    path('refresh-token/', views.refresh_access_token, name='refresh-token'),
    path('password-reset/', views.password_reset, name='password_reset'),
    path('verify-email/', views.verify_email, name='verify-email'),
    path('set-new-password/', views.set_new_password , name='set-new-password'),
    path('favorites/add/', views.add_to_favorites, name='add_to_favorites'),
    path('favorites/remove/', views.remove_from_favorites, name='remove_from_favorites'),
    path('favorites/', views.get_favorite_books, name='get_favorite_books'),

]
