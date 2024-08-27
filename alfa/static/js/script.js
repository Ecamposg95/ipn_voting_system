const video = document.getElementById('video');
const canvas = document.getElementById('canvas');
const context = canvas.getContext('2d');

navigator.mediaDevices.getUserMedia({ video: true })
    .then(stream => {
        video.srcObject = stream;
    })
    .catch(error => {
        console.error("Error accessing the camera: ", error);
    });

function capture() {
    context.drawImage(video, 0, 0, canvas.width, canvas.height);
    return canvas.toDataURL('image/jpeg');
}

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
