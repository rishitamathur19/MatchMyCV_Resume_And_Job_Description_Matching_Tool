from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('download-pdf/', views.download_pdf, name='download_pdf'),
]
