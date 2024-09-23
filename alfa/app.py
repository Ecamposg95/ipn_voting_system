import os
import datetime
import base64
import numpy as np
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import face_recognition
from io import BytesIO
from PIL import Image
import sqlite3

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Cambia esto a una clave secreta más segura en producción
app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(), 'static', 'uploads')
DATABASE = 'database.db'

# Crear la base de datos y las tablas necesarias si no existen
def init_db():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY, name TEXT, encoding BLOB)''')
    c.execute('''CREATE TABLE IF NOT EXISTS votes
                 (id INTEGER PRIMARY KEY, user_id INTEGER, candidate TEXT)''')
    conn.commit()
    conn.close()

# Ejecutar la inicialización de la base de datos
init_db()

# Decodificar la imagen recibida en base64
def decode_image(data_url):
    try:
        header, encoded = data_url.split(",", 1)
        data = base64.b64decode(encoded)
        image = Image.open(BytesIO(data))
        return image
    except Exception as e:
        print(f"Error decoding image: {e}")
        return None

# Guardar la imagen en el servidor
def save_image(image, filename):
    try:
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        image.save(filepath)
        return filepath
    except Exception as e:
        print(f"Error saving image: {e}")
        return None

# Guardar el encoding facial en la base de datos
def save_encoding(name, encoding):
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("INSERT INTO users (name, encoding) VALUES (?, ?)", (name, encoding.tobytes()))
    conn.commit()
    conn.close()

# Cargar los encodings faciales desde la base de datos
def load_encodings():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("SELECT name, encoding FROM users")
    users = c.fetchall()
    conn.close()
    return {name: np.frombuffer(enc, dtype=np.float64) for name, enc in users}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    name = data.get('name')
    photo_data_url = data.get('photo')
    if photo_data_url and name:
        if not os.path.exists(app.config['UPLOAD_FOLDER']):
            os.makedirs(app.config['UPLOAD_FOLDER'])

        image = decode_image(photo_data_url)
        if image:
            filename = f"{datetime.date.today()}_{name}.jpg"
            filepath = save_image(image, filename)
            if filepath:
                encoding = face_recognition.face_encodings(face_recognition.load_image_file(filepath))
                if encoding:
                    save_encoding(name, encoding[0])
                    return jsonify({"message": "Registro exitoso"}), 200
    return jsonify({"message": "Error en el registro"}), 400

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    photo_data_url = data.get('photo')
    if photo_data_url:
        if not os.path.exists(app.config['UPLOAD_FOLDER']):
            os.makedirs(app.config['UPLOAD_FOLDER'])

        image = decode_image(photo_data_url)
        if image:
            login_filename = os.path.join(app.config['UPLOAD_FOLDER'], "login_face.jpg")
            image.save(login_filename)

            login_image = face_recognition.load_image_file(login_filename)
            login_face_encodings = face_recognition.face_encodings(login_image)

            if len(login_face_encodings) > 0:
                login_face_encoding = login_face_encodings[0]
                registered_data = load_encodings()
                for name, registered_face_encoding in registered_data.items():
                    matches = face_recognition.compare_faces([registered_face_encoding], login_face_encoding)
                    if any(matches):
                        session['user_name'] = name
                        return jsonify({"success": True, "name": name})

        return jsonify({"success": False})
    return redirect(request.url)

@app.route('/success')
def success():
    user_name = session.get('user_name')
    if user_name:
        return render_template('success.html', user_name=user_name)
    return redirect(url_for('index'))

@app.route('/vote', methods=['GET', 'POST'])
def vote():
    if 'user_name' not in session:
        return redirect(url_for('index'))

    if request.method == 'POST':
        candidate = request.form.get('candidate')
        if candidate:
            conn = sqlite3.connect(DATABASE)
            c = conn.cursor()
            user_id = c.execute("SELECT id FROM users WHERE name = ?", (session['user_name'],)).fetchone()[0]
            c.execute("INSERT INTO votes (user_id, candidate) VALUES (?, ?)", (user_id, candidate))
            conn.commit()
            conn.close()
            return redirect(url_for('success'))

    return render_template('vote.html')

@app.route('/logout')
def logout():
    session.clear()  # Limpiar la sesión
    return redirect(url_for('index'))  # Redirigir a la página de inicio

if __name__ == '__main__':
    app.run(debug=True)
