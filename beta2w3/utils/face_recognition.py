import face_recognition
import pickle
import base64
import io
from PIL import Image

# Archivo de almacenamiento para datos de reconocimiento facial
FACIAL_DATA_PATH = "utils/facial_data.pkl"

# Cargar o inicializar los datos de reconocimiento facial
if FACIAL_DATA_PATH:
    with open(FACIAL_DATA_PATH, "rb") as f:
        facial_data = pickle.load(f)
else:
    facial_data = {}

# Función para convertir la imagen base64 a un encoding facial
def get_face_encoding_from_base64(image_base64):
    image_data = base64.b64decode(image_base64.split(",")[1])
    image = Image.open(io.BytesIO(image_data))
    image_np = face_recognition.load_image_file(image)
    encodings = face_recognition.face_encodings(image_np)
    return encodings[0] if encodings else None

# Registrar el usuario con el nombre y foto
def register_user(name, image_base64):
    encoding = get_face_encoding_from_base64(image_base64)
    if encoding:
        facial_data[name] = encoding
        with open(FACIAL_DATA_PATH, "wb") as f:
            pickle.dump(facial_data, f)
        return {"message": "Registro exitoso"}
    return {"message": "Error en el reconocimiento facial"}

# Autenticar el usuario con reconocimiento facial
def authenticate_user(name, image_base64):
    if name not in facial_data:
        return {"success": False, "message": "Usuario no registrado"}

    encoding = get_face_encoding_from_base64(image_base64)
    if encoding and face_recognition.compare_faces([facial_data[name]], encoding)[0]:
        return {"success": True}
    return {"success": False, "message": "No coincide la imagen"}
