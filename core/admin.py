from django.contrib import admin
from .models import Profile, Post, LikePost, Group

# Registrar el modelo Group
class GroupAdmin(admin.ModelAdmin):
    list_display = ('id', 'group_name', 'creator', 'created_at')
    search_fields = ('group_name', 'creator__username')
    list_filter = ('created_at',)

# Register your models here.
admin.site.register(Profile)
admin.site.register(Post)
admin.site.register(LikePost)
admin.site.register(Group, GroupAdmin)