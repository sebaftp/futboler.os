from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth.models import User, auth
from django.contrib import messages
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from itertools import chain
from .models import Profile, Post, LikePost, Group

# Create your views here.

# DEfinimos la url en la que el usuario sera redirigido si no a iniciado sesión
@login_required(login_url="signin")
def index(request):
    user_object = User.objects.get(username = request.user.username)
    user_profile = Profile.objects.get(user = user_object)

    posts = Post.objects.all()

    return render(request, 'index.html', {'user_profile': user_profile, 'posts': posts})

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
    username = request.user.username
    post_id = request.GET.get('post_id')

    post = Post.objects.get(id = post_id)

    like_filter = LikePost.objects.filter(post_id = post_id, username = username).first()

    if like_filter == None:
        new_like = LikePost.objects.create(post_id = post_id, username = username)
        new_like.save()
        post.no_of_likes = post.no_of_likes + 1
        post.save()
        return redirect('/')
    else:
        like_filter.delete()
        post.no_of_likes = post.no_of_likes - 1
        post.save()
        return redirect('/')

@login_required(login_url="signin")
def profile(request, pk):
    #Obtener el usuario del perfil basado en el `pk` (id o nombre de usuario)
    user_profile = get_object_or_404(Profile, user__username=pk) 
    user = user_profile.user

    #Obtener todas las publicaciones del usuario
    user_posts = Post.objects.filter(user=pk)

    # Obtener el número de publicaciones del usuario
    user_posts_length = len(user_posts)

    context = {
        'user_profile': user_profile,
        'user': user,
        'user_posts': user_posts,
        'user_posts_length': user_posts_length,
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
    # Obtener el usuario directamente del request
    user = request.user

    # Intentar obtener el grupo del cual el usuario es creador
    user_group = Group.objects.filter(creator=user).first()

    if request.method == 'POST':
        # Procesamiento de creación o actualización del grupo
        group_name = request.POST['group_name']
        bio = request.POST['bio']
        logo = request.FILES.get('logo') if request.FILES.get('logo') else (user_group.logo if user_group else None)
        banner = request.FILES.get('banner') if request.FILES.get('banner') else (user_group.banner if user_group else None)
        
        if user_group:
            # Actualizar el grupo existente
            user_group.group_name = group_name
            user_group.bio = bio
            user_group.logo = logo
            user_group.banner = banner
            user_group.save()
        else:
            # Crear un nuevo grupo
            Group.objects.create(
                creator=user,
                group_name=group_name,
                bio=bio,
                logo=logo,
                banner=banner,
            )
        return redirect('index')

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
    
def group_detail(request, id):
    group = get_object_or_404(Group, id=id)
    return render(request, 'groups.html', {'group': group})

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