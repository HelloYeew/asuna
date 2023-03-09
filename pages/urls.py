from django.urls import path

from pages import views

urlpatterns = [
    path('robots.txt', views.robots_txt, name='robots_txt'),
    path('', views.homepage, name='homepage')
]