from django.urls import path
from . import views

# Configuramos a donde nos lleva cada link
urlpatterns = [
    path('', views.index, name='index'),
    path('settings', views.settings, name='settings'),
    path('signup', views.signup, name='signup'),
    path('signin', views.signin, name='signin'),
    path('logout', views.logout, name='logout'),
]
