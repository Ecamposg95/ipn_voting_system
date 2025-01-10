import os
import pickle
import base64
import io
from flask import session
import face_recognition
from PIL import Image
import numpy as np

# Ruta para almacenar datos de reconocimiento facial de los votantes
FACIAL_DATA_PATH = "utils/facial_data.pkl"

# Cargar los datos faciales existentes o inicializar
if os.path.exists(FACIAL_DATA_PATH):
    with open(FACIAL_DATA_PATH, "rb") as f:
        facial_data = pickle.load(f)
else:
    facial_data = {}

# Función para convertir imagen base64 a encoding facial
def get_face_encoding_from_base64(image_base64):
    try:
        # Decodificar la imagen base64
        image_data = base64.b64decode(image_base64.split(",")[1])
        # Cargar la imagen en formato compatible con face_recognition
        image_np = face_recognition.load_image_file(io.BytesIO(image_data))
        # Obtener los encodings faciales
        encodings = face_recognition.face_encodings(image_np)
        return encodings[0] if encodings else None
    except Exception as e:
        print(f"Error al procesar la imagen base64: {e}")
        return None

# Autenticar al administrador con usuario y contraseña
def authenticate_admin(username, password):
    """Verifica las credenciales del administrador."""
    if username == "admin" and password == "123456":  # Cambiar por credenciales seguras
        session["authenticated"] = True
        session["is_admin"] = True
        return True
    return False

# Registrar nuevo votante con reconocimiento facial
def register_user(name, image_base64):
    """Registra un nuevo usuario con reconocimiento facial."""
    if name in facial_data:
        return {"message": "El usuario ya está registrado"}

    # Obtener el encoding facial de la imagen
    encoding = get_face_encoding_from_base64(image_base64)
    if encoding is not None:
        facial_data[name] = encoding
        # Guardar los datos faciales en un archivo
        with open(FACIAL_DATA_PATH, "wb") as f:
            pickle.dump(facial_data, f)
        session["authenticated"] = True
        session["role"] = "votante"
        return {"message": "Registro exitoso"}
    return {"message": "Error en el reconocimiento facial. Asegúrate de que la imagen sea válida."}

# Autenticar votante con reconocimiento facial
def authenticate_user(name, photo):
    """Autentica al usuario utilizando su nombre y una imagen."""
    if name not in facial_data:
        return {"success": False, "message": "Usuario no registrado"}

    # Obtener el encoding de la imagen capturada
    encoding = get_face_encoding_from_base64(photo)
    if encoding is None:
        return {"success": False, "message": "No se pudo procesar la imagen enviada."}

    # Comparar el encoding con los datos almacenados
    try:
        matches = face_recognition.compare_faces([facial_data[name]], encoding)
        if any(matches):
            session["authenticated"] = True
            session["role"] = "votante"
            return {"success": True, "message": "Autenticación exitosa"}
    except Exception as e:
        print(f"Error durante la comparación facial: {e}")
    
    return {"success": False, "message": "No se pudo autenticar con reconocimiento facial"}

# Cerrar sesión del usuario
def logout_user():
    """Elimina todos los datos de sesión del usuario."""
    session.pop("authenticated", None)
    session.pop("is_admin", None)
    session.pop("role", None)
