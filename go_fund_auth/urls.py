# MyDjangoApp/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register', views.register, name='register'),
    path('login', views.user_login, name='login'),
    path('profile/', views.profile, name='profile'),
    path('edit_profile/', views.edit_profile, name='edit_profile'),
    path('logout', views.user_logout, name='logout'),
    path('delete_account/', views.delete_account, name='delete_account'),
    path('activate/<str:uidb64>/<str:token>',
         views.activate_account, name='activate'),
    path('reset_password/<str:uidb64>/<str:token>',
         views.reset_password, name='reset_password'),
    path('reset_password_sent/', views.password_reset_sent,
         name='password_reset_sent'),
    path('account_activation_sent/', views.account_activation_sent,
         name='account_activation_sent'),
    path('account_activation_complete/', views.account_activation_complete,
         name='account_activation_complete'),
    path('forgot-password/', views.forgot_password, name='forgot_password'),

]
