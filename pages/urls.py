from django.urls import path

from pages import views

urlpatterns = [
    path('', views.homepage, name='homepage')
]