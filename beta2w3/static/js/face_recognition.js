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
            alert("No se pudo acceder a la cámara. Asegúrate de que tu dispositivo tenga una cámara funcional.");
        });
}

// Activar la cámara para los elementos de video de registro e inicio de sesión
if (videoElements.register) activateCamera(videoElements.register);
if (videoElements.login) activateCamera(videoElements.login);

// Función para capturar la imagen desde el video y devolverla en formato base64
function captureImage(videoElement) {
    try {
        context.drawImage(videoElement, 0, 0, canvas.width, canvas.height);
        return canvas.toDataURL('image/jpeg'); // Devuelve la imagen en base64
    } catch (error) {
        console.error("Error al capturar la imagen: ", error);
        alert("Error al capturar la imagen. Intenta nuevamente.");
        return null;
    }
}

// Función para registrar al usuario con reconocimiento facial
async function register() {
    const name = document.getElementById('register-name').value;
    const address = document.getElementById('address').value;

    if (!name || !address) {
        alert("Por favor, completa todos los campos.");
        return;
    }

    const photo = captureImage(videoElements.register);
    if (!photo) return;

    try {
        const response = await fetch('/auth/register', { // Ajuste en la ruta
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ name, address, photo })
        });
        const data = await response.json();
        if (response.ok) {
            alert('Registro exitoso. Redirigiendo al inicio de sesión.');
            window.location.href = data.redirect || '/auth/voter_login'; // Ruta por defecto
        } else {
            alert(data.error || 'Error en el registro. Inténtalo nuevamente.');
        }
    } catch (error) {
        console.error("Error en el registro:", error);
        alert("Hubo un error en el registro. Intenta nuevamente más tarde.");
    }
}

// Función para iniciar sesión del usuario votante
async function login() {
    const name = document.getElementById('login-name').value;

    if (!name) {
        alert("Por favor, ingresa tu nombre.");
        return;
    }

    const photo = captureImage(videoElements.login);
    if (!photo) return;

    try {
        const response = await fetch('/auth/voter_login', { // Ajuste en la ruta
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ name, photo })
        });
        const data = await response.json();
        if (response.ok) {
            alert('Inicio de sesión exitoso.');
            window.location.href = data.redirect || '/voter/dashboard'; // Ruta por defecto
        } else {
            alert(data.error || 'Error en la autenticación. Inténtalo de nuevo.');
        }
    } catch (error) {
        console.error("Error en el inicio de sesión:", error);
        alert("Hubo un error en el inicio de sesión. Intenta nuevamente más tarde.");
    }
}

// Asignar eventos de clic a los botones de registro e inicio de sesión
document.getElementById('register-button')?.addEventListener('click', register);
document.getElementById('login-button')?.addEventListener('click', login);
