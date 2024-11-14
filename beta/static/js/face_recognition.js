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
    const address = document.getElementById('address').value;
    const photo = captureImage(videoElements.register);

    try {
        const response = await fetch('/register', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ name, address, photo })
        });
        const data = await response.json();
        if (response.ok) {
            alert('Registro exitoso');
            window.location.href = data.redirect;
        } else {
            alert(data.message || 'Error en el registro');
        }
    } catch (error) {
        console.error("Error:", error);
    }
}

// Función para iniciar sesión del usuario votante
async function login() {
    const name = document.getElementById('login-name').value;
    const photo = captureImage(videoElements.login);

    try {
        const response = await fetch('/votante_login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ name, photo })
        });
        const data = await response.json();
        if (response.ok) {
            window.location.href = data.redirect;
        } else {
            alert(data.message || 'Error en la autenticación. Inténtalo de nuevo.');
        }
    } catch (error) {
        console.error("Error:", error);
    }
}

// Asignar eventos de clic a los botones de registro e inicio de sesión
document.getElementById('register-button')?.addEventListener('click', register);
document.getElementById('login-button')?.addEventListener('click', login);
