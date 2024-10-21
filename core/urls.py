from django.urls import path
from . import views

# Configuramos a donde nos lleva cada link
urlpatterns = [
    path('', views.index, name='index'),
    path('signup', views.signup, name='signup'),
]
