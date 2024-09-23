const video = document.getElementById('video');
const canvas = document.getElementById('canvas');
const context = canvas.getContext('2d');

// Acceso a la cámara
navigator.mediaDevices.getUserMedia({ video: true })
    .then(stream => {
        video.srcObject = stream;
    })
    .catch(error => {
        console.error("Error accessing the camera: ", error);
    });

// Función para capturar la imagen desde el video
function capture() {
    context.drawImage(video, 0, 0, canvas.width, canvas.height);
    return canvas.toDataURL('image/jpeg');
}

// Función para registrar al usuario
async function register() {
    const name = document.getElementById('name').value;
    const photo = capture();

    try {
        const response = await fetch('/register', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ name, photo })
        });
        const data = await response.json();
        if (data.message === "Registro exitoso") {
            alert('Registro exitoso');
        } else {
            alert('Error en el registro');
        }
    } catch (error) {
        console.error("Error:", error);
    }
}

// Función para iniciar sesión
async function login() {
    const photo = capture();

    try {
        const response = await fetch('/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ photo })
        });
        const data = await response.json();
        if (data.success) {
            window.location.href = `/success?user_name=${data.name}`;
        } else {
            alert('No se encontró ninguna coincidencia');
        }
    } catch (error) {
        console.error("Error:", error);
    }
}

// Función para cerrar sesión
function logout() {
    window.location.href = "/logout";
}
