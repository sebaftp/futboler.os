from django.db import models
from django.contrib.auth import get_user_model
import uuid
from datetime import datetime

User = get_user_model()

class Group(models.Model):
    id_group = models.AutoField(primary_key=True)
    group_name = models.CharField(max_length=100, unique=True)
    bio = models.TextField(blank=True)
    logo = models.ImageField(upload_to='group_logos', default='default_logo.jpg')
    banner = models.ImageField(upload_to='group_banners', default='default_banner.jpg')
    created_at = models.DateTimeField(auto_now_add=True)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name="created_groups")

    def __str__(self):
        return self.group_name

class Profile(models.Model):
    POSICIONES = [
        ('PT', 'Portero'),
        ('DF', 'Defensa'),
        ('CC', 'Centrocampista'),
        ('DL', 'Delantero'),
    ]

    # Relationships
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    groups = models.ManyToManyField(Group, related_name="members", blank=True)

    # Profile attributes
    id_user = models.IntegerField()
    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)
    bio = models.TextField(blank=True)
    profileimg = models.ImageField(upload_to='profile_images', default='blank_pfp.jpg')
    location = models.CharField(max_length=100, blank=True)
    posicion_preferida = models.CharField(max_length=2, choices=POSICIONES, blank=True)
    age = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.user.username
    
class Post(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    user = models.CharField(max_length=100)
    image = models.ImageField(upload_to='post_images')
    caption = models.TextField()
    created_at = models.DateTimeField(default=datetime.now)
    no_of_likes = models.IntegerField(default=0)

    def __str__(self):
        return self.user
    
class LikePost(models.Model):
    post_id = models.CharField(max_length=500)
    username = models.CharField(max_length=100)

    def __str__(self):
        return self.username
