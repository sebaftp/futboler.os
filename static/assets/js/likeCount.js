document.addEventListener('DOMContentLoaded', function() {

    // Obtener el token CSRF
    function getCookie(name) {
        // Creamos la variable para almacenar la cookie
        let cookieValue = null;
        // Si hay cookies y la cookie no esta vacia hacemos lo siguiente
        if (document.cookie && document.cookie !== '') {
            // Separamos las cookies por ;
            const cookies = document.cookie.split(';');
            // Leemos cada cookie por separado
            for (let i = 0; i < cookies.length; i++) {
                // Separamos cada cookie por =
                const cookie = cookies[i].trim();
                // Si la cookie empieza con el nombre de la cookie que estamos buscando
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    // Asignamos el valor de la cookie a la variable cookieValue
                    cookieValue = decodeURIComponent(cookie.substring(name.length +1));
                    break;
                }
            }
        }
        // Retornamos el valor de la cookie
        return cookieValue;
    }

    // Obtenemos el token CSRF
    const csrftoken = getCookie('csrftoken');

    // Recuperamos los botones de like
    const likeButtons = document.querySelectorAll('.like-post-btn');

    // Recorremos cada boton de like
    likeButtons.forEach(button => {
        // Añadimos un evento click a cada boton
        button.addEventListener('click', function(e) {
            // Prevenimos que el boton se ejecute
            e.preventDefault();
            // Obtenemos el id del post
            const postId = this.dataset.postId;
            // Obtenemos el elemento que contiene el numero de likes
            const likecount = this.querySelector('.Like-count');

            // Realizar solicitud AJAX
            // AJAX (Asynchronous JavaScript And XML) es una técnica que permite hacer peticiones al servidor
            // y actualizar partes de una página web sin necesidad de recargarla completamente.
            fetch(`/like-post?post_id=${postId}`, {
                method: 'GET',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': csrftoken,
                },
            })
            // Convertimos la respuesta a JSON
            .then(response => response.json())
            // Si la solicitud fue exitosa, actualizamos el numero de likes
            .then(data => {
                // verificar si la solicitud fue exitosa
                if (data.status == 'success') {
                    if (data.likes === 0) {
                        likecount.textContent = 'Sin likes';
                    } else if (data.likes === 1) {
                        likecount.textContent = `Le ha gustado a ${data.likes} persona`;
                    } else {
                        likecount.textContent = `Le ha gustado a ${data.likes} personas`;
                    }
                }
            })
            // Si ocurre un error, lo mostramos en la consola
            .catch(error = console.error('Error:', error ));
        });
    });
});
