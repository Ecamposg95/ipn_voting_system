// Acceso a la cámara
const videoElements = {
    register: document.getElementById('register-video'),
    login: document.getElementById('login-video')
};
const canvas = document.getElementById('canvas');
const context = canvas.getContext('2d');

// Función para activar la cámara en el video correspondiente
function activateCamera(videoElement) {
    navigator.mediaDevices.getUserMedia({ video: true })
        .then(stream => {
            videoElement.srcObject = stream;
        })
        .catch(error => {
            console.error("Error al acceder a la cámara: ", error);
        });
}

// Activar la cámara para los elementos de video de registro e inicio de sesión
if (videoElements.register) activateCamera(videoElements.register);
if (videoElements.login) activateCamera(videoElements.login);

// Función para capturar la imagen desde el video y devolverla en formato base64
function captureImage(videoElement) {
    context.drawImage(videoElement, 0, 0, canvas.width, canvas.height);
    return canvas.toDataURL('image/jpeg'); // Devuelve la imagen en base64
}

// Función para registrar al usuario con reconocimiento facial
async function register() {
    const name = document.getElementById('register-name').value;
    const photo = captureImage(videoElements.register);

    try {
        const response = await fetch('/auth/register', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ name, photo })
        });
        const data = await response.json();
        if (data.message === "Registro exitoso") {
            alert('Registro exitoso');
            window.location.href = '/auth/user_login'; // Redirigir a login después de registrarse
        } else {
            alert(data.message || 'Error en el registro');
        }
    } catch (error) {
        console.error("Error:", error);
    }
}

// Función para iniciar sesión del usuario
async function login() {
    const name = document.getElementById('login-name').value;
    const photo = captureImage(videoElements.login);

    try {
        const response = await fetch('/auth/user_login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ name, photo })
        });
        const data = await response.json();
        if (data.success) {
            window.location.href = '/user/dashboard';
        } else {
            alert(data.message || 'Error en la autenticación. Inténtalo de nuevo.');
        }
    } catch (error) {
        console.error("Error:", error);
    }
}


// Función para generar dinámicamente los campos de opciones en el formulario de creación de votación
function generateOptionsFields() {
    const container = document.getElementById('opciones_container');
    container.innerHTML = '';  // Limpiar campos anteriores
    const numOptions = document.getElementById('num_opciones').value;

    if (numOptions < 2 || numOptions > 6) {
        alert("Por favor, seleccione un número de opciones entre 2 y 6.");
        return;
    }

    for (let i = 1; i <= numOptions; i++) {
        const label = document.createElement('label');
        label.textContent = `Opción ${i}:`;
        const input = document.createElement('input');
        input.type = 'text';
        input.name = 'opciones[]';
        input.required = true;
        input.placeholder = `Ingrese el texto para la opción ${i}`;
        
        container.appendChild(label);
        container.appendChild(input);
        container.appendChild(document.createElement('br'));
    }
}

// Agregar el evento de inicio de sesión al botón correspondiente en el HTML
document.getElementById('login-button').addEventListener('click', login);
document.getElementById('register-button').addEventListener('click', register);
