from django.shortcuts import render, redirect
from django.contrib.auth.models import User, auth
from django.contrib import messages
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from .models import Profile

# Create your views here.

# DEfinimos la url en la que el usuario sera redirigido si no a iniciado sesión
@login_required(login_url="signin")
def index(request):
    return render(request, 'index.html')

@login_required(login_url="signin")
def settings(request):
    user_profile = Profile.objects.get(user = request.user)

    if request.method == 'POST':

        # Si no hay una imagen de perfil enviada atraves del formulario:
        if request.FILES.get('image') == None:
            image = user_profile.profileimg
            bio = request.POST['bio']
            location = request.POST['location']
            edad = request.POST['age']
            posicion = request.POST['posicion_preferida']

            user_profile.profileimg = image
            user_profile.bio = bio
            user_profile.location = location
            user_profile.age = edad
            user_profile.posicion_preferida = posicion
            user_profile.save()

        if request.FILES.get('image') != None:

            image = request.FILES.get('image')
            bio = request.POST['bio']
            location = request.POST['location']
            edad = request.POST['age']
            posicion = request.POST['posicion_preferida']

            user_profile.profileimg = image
            user_profile.bio = bio
            user_profile.location = location
            user_profile.age = edad
            user_profile.posicion_preferida = posicion
            user_profile.save()

        return redirect('settings')


    return render(request, 'setting.html', {'user_profile': user_profile})

def signup(request):

    # Registramos el usuario de usuario :0
    if request.method == 'POST':
        username = request.POST['username']
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