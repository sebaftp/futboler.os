from django.db import models
from django.db.models import Q
from django.contrib.auth import get_user_model
import uuid
from datetime import datetime

User = get_user_model()

class Group(models.Model):
    id = models.AutoField(primary_key=True)
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    group_name = models.CharField(max_length=100)
    bio = models.TextField(blank=True)
    logo = models.ImageField(upload_to='group_logos', default='default_logo.png')
    banner = models.ImageField(upload_to='group_banners', default='default_banner.png')
    created_at = models.DateTimeField(auto_now_add=True)

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

class ThreadManager(models.Manager):
    def by_user(self, **kwargs):
        user = kwargs.get('user')
        lookup = Q(first_person=user) | Q(second_person=user)
        qs = self.get_queryset().filter(lookup).distinct()
        return qs

class Thread(models.Model):
    first_person  = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name='thread_first_person')
    second_person  = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name='thread_second_person')
    updated = models.DateTimeField(auto_now=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    objects = ThreadManager()

    class Meta:
        unique_together = ['first_person', 'second_person']

class ChatMessage(models.Model):
    thread = models.ForeignKey(Thread, on_delete=models.CASCADE, null=True, blank=True, related_name='chatmessage_thread')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

class Equipo(models.Model):
    nombre = models.CharField(max_length=100)
    logo = models.ImageField(upload_to="logos_equipos", null=True, blank=True)

    def __str__(self):
        return self.nombre

class Partido(models.Model):
    equipo1 = models.ForeignKey(Equipo, on_delete=models.CASCADE, related_name="partidos_equipo1")
    equipo2 = models.ForeignKey(Equipo, on_delete=models.CASCADE, related_name="partidos_equipo2")
    goles_equipo1 = models.IntegerField(default=0)
    goles_equipo2 = models.IntegerField(default=0)
    fecha = models.DateField()

    def __str__(self):
        return f"{self.equipo1} vs {self.equipo2}"

class Reporte(models.Model):
    MOTIVOS_REPORTE = [
        ('spam', 'Spam'),
        ('abuso', 'Abuso'),
        ('contenido_inapropiado', 'Contenido Inapropiado'),
        ('otro', 'Otro'),
    ]

    user_report = models.ForeignKey(User, related_name="reportes_recibidos", on_delete=models.CASCADE)
    usuario = models.ForeignKey(User, related_name="reportes_enviados", on_delete=models.CASCADE, null=True, blank=True)
    motivo = models.CharField(max_length=50, choices=MOTIVOS_REPORTE)
    descripcion = models.TextField()
    fecha_reporte = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Reporte por {self.usuario.username if self.usuario else 'Anonimo'} - {self.motivo}"

