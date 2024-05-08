from django.urls import path
from app import views

urlpatterns = [
    path("", views.index, name="index"),
    path("product/<int:id>", views.detail, name="detail"),
]
