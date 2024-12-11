from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
import json
from django.urls import reverse
from django.contrib.auth.models import User, auth
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from itertools import chain
from django.db.models import Q
from .models import Profile, Post, LikePost, Group, Thread, ChatMessage, Partido, Reporte, Notification
from django.views.decorators.csrf import csrf_exempt

# Create your views here.

def group_detail(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    # Filtramos las notificaciones no leídas de este usuario
    notifications = Notification.objects.filter(receiver=request.user, is_read=False)

    context = {
        'group': group,
        'notifications': notifications,
    }

    return render(request, 'groups.html', context)
def invite_user(request, group_id):
    group = get_object_or_404(Group, id=group_id)  # Verifica que el grupo exista
    if request.method == 'POST':
        email = request.POST.get('email')
        # Lógica para enviar la invitación
        messages.success(request, f"Se ha enviado la invitación a {email} para el grupo {group.group_name}.")
        return redirect('groups', id=group_id)
    return render(request, 'invite_user.html', {'group': group})
# DEfinimos la url en la que el usuario sera redirigido si no a iniciado sesión
@login_required(login_url="signin")
def index(request):
    try:
        user_object = User.objects.get(username=request.user.username)
        print(f"Usuario encontrado: {user_object.username}")
        
        try:
            user_profile = Profile.objects.get(user=user_object)
            print(f"Perfil encontrado: {user_profile.id}")
        except Profile.DoesNotExist:
            print(f"No se encontró perfil para el usuario {user_object.username}")
            print("Perfiles existentes:", Profile.objects.all().values_list('user__username', flat=True))
            # Podemos ver si hay algún problema con el id_user
            print(f"ID del usuario: {user_object.id}")
            
            # Intentar buscar el perfil por id_user
            profile_by_id = Profile.objects.filter(id_user=user_object.id).first()
            if profile_by_id:
                print(f"Se encontró perfil por id_user: {profile_by_id.id}")
            
            raise  # Re-lanza la excepción original
        
        posts = Post.objects.all()
        return render(request, 'index.html', {'user_profile': user_profile, 'posts': posts})
        
    except Exception as e:
        print(f"Error: {str(e)}")
        raise

@login_required(login_url="signin")
def upload(request):
    if request.method == 'POST':
        user = request.user.username
        image = request.FILES.get('image_upload')
        caption = request.POST['caption']

        new_post = Post.objects.create(user = user, image = image, caption = caption)
        new_post.save()
        
        return redirect('/')
    else:
        return redirect('/')

@login_required(login_url="signin")
def search(request):
    # Obtenemos el usuario actual
    user_object = User.objects.get(username = request.user.username)
    user_profile = Profile.objects.get(user = user_object)

    # Si el método de la solicitud es POST
    if request.method == 'POST':
        username = request.POST['username']
        username_object = User.objects.filter(username__icontains = username)

        # Creamos listas para almacenar los IDs de usuario y los perfiles de usuario
        username_profile = []
        username_profile_list = []

        # Iteramos sobre los objetos de usuario encontrados
        for users in username_object:
            username_profile.append(users.id)

        for ids in username_profile:
            profile_list = Profile.objects.filter(id_user = ids)
            username_profile_list.append(profile_list)

        username_profile_list = list(chain(*username_profile_list))

        return render(request, 'search.html', {'user_profile': user_profile, 'username_profile_list': username_profile_list})

@login_required(login_url="signin")
def like_post(request):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        username = request.user.username
        post_id = request.GET.get('post_id')
        
        post = Post.objects.get(id = post_id)

        like_filter = LikePost.objects.filter(post_id = post_id, username = username).first()

        if like_filter == None:
            new_like = LikePost.objects.create(post_id = post_id, username = username)
            new_like.save()
            post.no_of_likes = post.no_of_likes + 1
            post.save()
        else:
            like_filter.delete()
            post.no_of_likes = post.no_of_likes - 1
            post.save()

        return JsonResponse({
            "status": "success",
            "likes": post.no_of_likes
        })
    return redirect('/')


@login_required(login_url="signin")
def profile(request, pk):
    # Obtener el perfil del usuario logueado (para la barra de navegación)
    logged_user_profile = Profile.objects.get(user=request.user)
    
    # Obtener el perfil que se está visitando
    user_profile = get_object_or_404(Profile, user__username=pk) 
    user = user_profile.user

    # Obtener todas las publicaciones del usuario
    user_posts = Post.objects.filter(user=pk)

    context = {
        'logged_user_profile': logged_user_profile,  # Perfil del usuario logueado
        'user_profile': user_profile,                # Perfil que se está visitando
        'user': user,
        'user_posts': user_posts,
        'user_posts_length': len(user_posts),
    }
    return render(request, 'profile.html', context)

@login_required(login_url="signin")
def settings(request):
    user_profile = Profile.objects.get(user = request.user)
    user = User.objects.get(username = request.user.username)

    if request.method == 'POST':

        # Si no hay una imagen de perfil enviada atraves del formulario:
        if request.FILES.get('image') == None:
            first_name = request.POST['first_name']
            last_name = request.POST['last_name']
            image = user_profile.profileimg
            bio = request.POST['bio']
            location = request.POST['location']
            edad = request.POST['age']
            posicion = request.POST['posicion_preferida']

            user.first_name = first_name # actualizamos el nombre del usuario
            user.last_name = last_name # actualizamos el apellido del usuario
            user.save()
            user_profile.profileimg = image
            user_profile.bio = bio
            user_profile.location = location
            user_profile.age = edad
            user_profile.posicion_preferida = posicion
            user_profile.save()

        if request.FILES.get('image') != None:

            first_name = request.POST['first_name']
            last_name = request.POST['last_name']
            image = request.FILES.get('image')
            bio = request.POST['bio']
            location = request.POST['location']
            edad = request.POST['age']
            posicion = request.POST['posicion_preferida']
            
            user.first_name = first_name # actualizamos el nombre del usuario
            user.last_name = last_name # actualizamos el apellido del usuario
            user.save()
            user_profile.profileimg = image
            user_profile.bio = bio
            user_profile.location = location
            user_profile.age = edad
            user_profile.posicion_preferida = posicion
            user_profile.save()

        return redirect('index')


    return render(request, 'setting.html', {'user_profile': user_profile})

@login_required(login_url="signin")
def groupsetting(request):
    user = request.user
    user_group = Group.objects.filter(creator=user).first()

    if request.method == 'POST':
        try:
            group_name = request.POST['group_name']
            bio = request.POST['bio']
            logo = request.FILES.get('logo') if request.FILES.get('logo') else (user_group.logo if user_group else None)
            banner = request.FILES.get('banner') if request.FILES.get('banner') else (user_group.banner if user_group else None)
            
            print(f"Creando grupo: {group_name}")  # Log
            
            if user_group:
                # Actualizar grupo existente
                user_group.group_name = group_name
                user_group.bio = bio
                user_group.logo = logo
                user_group.banner = banner
                user_group.save()
                print(f"Grupo actualizado: {user_group.id}")  # Log
            else:
                # Crear nuevo grupo
                user_group = Group.objects.create(
                    creator=user,
                    group_name=group_name,
                    bio=bio,
                    logo=logo,
                    banner=banner,
                )
                print(f"Nuevo grupo creado: {user_group.id}")  # Log
                
                user.profile.groups.add(user_group)
                print("Usuario añadido al grupo")  # Log

            return redirect(reverse('group_detail', args=[user_group.id]))
        except Exception as e:
            print(f"Error al crear/actualizar grupo: {str(e)}")  # Log error
            raise e

    return render(request, 'groupsetting.html', {'user_profile': user.profile, 'user_group': user_group})

@login_required(login_url="signin")
def my_team(request):
    user_profile = Profile.objects.get(user=request.user)

    # Verificamos si el usuario pertenece a algún grupo
    user_group = user_profile.groups.first()  # Asegúrate de que la relación esté configurada correctamente

    if user_group:
        # Si pertenece a un grupo, redirige a la página del perfil del equipo
        return redirect(reverse('group_detail', args=[user_group.id]))  # Ajusta 'group_detail' al nombre de tu URL
    else:
        # Si no pertenece a un grupo, redirige a la configuración de creación de equipo
        return redirect('groupsetting')

@login_required(login_url="signin")
def group_detail(request, id):
    group = get_object_or_404(Group, id=id)
    user_profile = Profile.objects.get(user=request.user)

    # Check if the current user is the creator of the group
    is_creator = (group.creator == request.user)

    context = {
        'group': group,
        'user_profile': user_profile,
        'is_creator': is_creator,
    }
    return render(request, 'groups.html', context)

@login_required(login_url="signin")
def delete_group(request, id):
    group = get_object_or_404(Group, id=id)

    if group.creator == request.user:
        group.delete()
        messages.success(request, "Grupo eliminado con éxito.")
        return redirect('index')
    else:
        messages.error(request, "No tienes permisos para eliminar este grupo.")
        return redirect('index')
    

def signup(request):
    # Registramos el usuario de usuario :0
    if request.method == 'POST':
        username = request.POST['username']
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        email = request.POST['email']
        password = request.POST['password']
        password2 = request.POST['password2']
        age = request.POST['age']

        if password == password2:
            if User.objects.filter(email = email).exists():
                messages.info(request, 'Correo ya registrado')
                return redirect('signup')
            elif User.objects.filter(username = username).exists():
                messages.info(request, "Ya existe este usuario!")
                return redirect('signup')
            else:
                user = User.objects.create_user(username=username,
                                                first_name=first_name,
                                                last_name=last_name,
                                                email=email,
                                                password=password)
                user.save()

                # Logear al usuario y llevarlo a la pagina de configuración
                user_login = auth.authenticate(username = username,
                                               password = password)
                auth.login(request, user_login)

                # Creamos el perfil del usuario registrado

                user_model = User.objects.get(username=username) # obtenemos el usuario de la tabla de usuarios
                new_profile = Profile.objects.create(user=user_model, id_user=user_model.id, age=age)
                new_profile.save()
                return redirect('settings')
        else:
            messages.info(request, "Las contraseñas no coinciden")
            return redirect('signup')

    else:
        return render(request, 'signup.html')
    
def signin(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = auth.authenticate(username = username,
                                 password = password)
        
        if user is not None:
            auth.login(request, user)
            return redirect('/')
        else:
            messages.info(request, 'Datos incorrectos')
            return redirect('signin')
        
    return render(request, 'signin.html')

@login_required(login_url="signin")
def logout(request):
    auth.logout(request)
    return redirect('signin')

# Vista de Chats
@login_required(login_url="signin")
def messages_page(request):
    threads = Thread.objects.filter(
        Q(first_person=request.user) | 
        Q(second_person=request.user)
    ).prefetch_related('chatmessage_thread').order_by('-updated')
    
    context = {
        'Thread': threads
    }
    return render(request, 'messages.html', context)

def history(request):
    partidos = Partido.objects.all().order_by('-fecha')  # Ordena por fecha
    return render(request, 'history.html', {'partidos': partidos})

def report_view(request, user_report_id):
    usuario_reportado = get_object_or_404(User, id=user_report_id)
    perfil_reportado = get_object_or_404(Profile, user=usuario_reportado)
    
    if request.method == 'POST':
        motivo = request.POST.get('motivo')
        descripcion = request.POST.get('descripcion')

        reporte = Reporte(
            usuario=request.user if request.user.is_authenticated else None,
            user_report=usuario_reportado,
            motivo=motivo,
            descripcion=descripcion
        )
        reporte.save()
        
        messages.success(request, '¡Reporte enviado con éxito!')
    
    return render(request, 'report.html', {
        'usuario_reportado': usuario_reportado,
        'perfil_reportado': perfil_reportado
    })
    
def search_users(request):
    query = request.GET.get('query', '')
    if query:
        users = User.objects.filter(
            Q(username__icontains=query) | Q(first_name__icontains=query) | Q(last_name__icontains=query)
        ).values('id', 'username', 'first_name', 'last_name')
        return JsonResponse({'users': list(users)})
    return JsonResponse({'users': []})


def send_invitation(request, group_id):
    if request.method == 'POST':
        group = get_object_or_404(Group, id=group_id)
        username = request.POST.get('username') or json.loads(request.body).get('username')
        invited_user = get_object_or_404(User, username=username)

        # Crear la notificación
        Notification.objects.create(
            sender=request.user,
            receiver=invited_user,
            group=group,
            message=f"@{request.user.username} te ha invitado a unirte a su equipo '{group.group_name}'."
        )

        return JsonResponse({'message': f'Invitación enviada a {username}.'})


@csrf_exempt
def respond_to_invitation(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        notification_id = data.get('notification_id')
        response = data.get('response')

        notification = get_object_or_404(Notification, id=notification_id)

        if response == 'accept':
            # Lógica para agregar al usuario al grupo
            notification.group.members.add(notification.receiver)
            notification.accepted = True
        elif response == 'reject':
            notification.accepted = False

        notification.is_read = True
        notification.save()

        return JsonResponse({'message': f'Invitación {"aceptada" if response == "accept" else "rechazada"}.'})

def group_view(request):
    group = Group.objects.filter(members=request.user).first()
    is_creator = group.creator == request.user if group else False
    user_profile = Profile.objects.get(user=request.user)

    return render(request, 'groupsetting.html', {
        'group': group,
        'is_creator': is_creator,
        'user_profile': user_profile,
    })
def create_group_view(request):
    if request.method == 'POST':
        form = GroupForm(request.POST, request.FILES)
        if form.is_valid():
            group = form.save(commit=False)
            group.creator = request.user
            group.save()
            return redirect('group_profile', group_id=group.id)
    else:
        form = GroupForm()
    return render(request, 'groupsetting.html', {'form': form})