import os
import base64
from PIL import Image
from io import BytesIO
from config import Config

def decode_image(data_url):
    try:
        header, encoded = data_url.split(",", 1)
        data = base64.b64decode(encoded)
        image = Image.open(BytesIO(data))
        return image
    except Exception as e:
        print(f"Error decoding image: {e}")
        return None

def save_image(image, filename):
    try:
        if not os.path.exists(Config.UPLOAD_FOLDER):
            os.makedirs(Config.UPLOAD_FOLDER)
        filepath = os.path.join(Config.UPLOAD_FOLDER, filename)
        image.save(filepath)
        return filepath
    except Exception as e:
        print(f"Error saving image: {e}")
        return None
