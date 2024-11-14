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
    image_data = base64.b64decode(image_base64.split(",")[1])  # Decodifica la imagen base64
    image_np = face_recognition.load_image_file(io.BytesIO(image_data))  # Convertir a imagen compatible con face_recognition
    encodings = face_recognition.face_encodings(image_np)
    return encodings[0] if encodings else None

# Autenticar al administrador con usuario y contraseña
def authenticate_admin(username, password):
    if username == "admin" and password == "123456":  # Cambiar según las credenciales
        session["authenticated"] = True
        session["is_admin"] = True
        return True
    return False

# Registrar nuevo votante con reconocimiento facial
def register_user(name, image_base64):
    encoding = get_face_encoding_from_base64(image_base64)
    if encoding is not None:  # Verificar que encoding no esté vacío
        facial_data[name] = encoding
        with open(FACIAL_DATA_PATH, "wb") as f:
            pickle.dump(facial_data, f)
        session["authenticated"] = True
        session["role"] = "votante"
        return {"message": "Registro exitoso"}
    return {"message": "Error en el reconocimiento facial"}

# Autenticar votante con reconocimiento facial
def authenticate_user(name, photo):
    if name not in facial_data:
        return {"success": False, "message": "Usuario no registrado"}

    # Obtener el encoding de la foto enviada
    encoding = get_face_encoding_from_base64(photo)
    
    # Verificar que encoding es un array válido
    if isinstance(encoding, np.ndarray) and encoding.size > 0:
        matches = face_recognition.compare_faces([facial_data[name]], encoding)
        if any(matches):  # Evalúa si al menos una comparación es verdadera
            session["authenticated"] = True
            session["role"] = "votante"
            return {"success": True, "message": "Autenticación exitosa"}
    return {"success": False, "message": "No se pudo autenticar con reconocimiento facial"}

# Cerrar sesión del usuario
def logout_user():
    session.pop("authenticated", None)
    session.pop("is_admin", None)
    session.pop("role", None)
