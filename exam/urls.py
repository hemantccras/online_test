# urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('', views.dashboard, name='dashboard'),
    path('test/', views.take_test, name='take_test'),
    path('certificate/', views.certificate, name='certificate'),
]