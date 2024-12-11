from django.urls import path
from django.conf.urls.static import static
from django.conf import settings
from . import views

# Configuramos a donde nos lleva cada link
urlpatterns = [
    path('', views.index, name='index'),
    path('invite/<int:group_id>/', views.invite_user, name='invite_user'),
    path('search-users/', views.search_users, name='search_users'),
    path('send-invitation/<int:group_id>/', views.send_invitation, name='send_invitation'),
    path('respond-to-invitation/', views.respond_to_invitation, name='respond_to_invitation'),
    path('settings', views.settings, name='settings'),
    path('my_team/', views.my_team, name='my_team'),
    path('search', views.search, name='search'),
    path('groups/<int:id>/', views.group_detail, name='group_detail'),
    path('delete_group/<int:id>/', views.delete_group, name='delete_group'),
    path('groupsetting', views.groupsetting, name='groupsetting'),
    path('upload', views.upload, name='upload'),
    path('profile/<str:pk>', views.profile, name='profile'),
    path('like-post', views.like_post, name='like-post'),
    path('signup', views.signup, name='signup'),
    path('signin', views.signin, name='signin'),
    path('logout', views.logout, name='logout'),
    path('chat', views.messages_page, name='messages'),
    path('history', views.history, name='history'),
    path('report/<int:user_report_id>/', views.report_view, name='report'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
