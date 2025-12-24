from django.urls import path
from . import views

urlpatterns = [
    path('test/', views.test_api),         # optional test API
    path('register/', views.register),     # register API
    path('login/', views.login),           # login API
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('reset-password/', views.reset_password, name='reset_password'),

]
