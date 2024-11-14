from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from .models import Usuario, db
import face_recognition
import numpy as np
import base64
from io import BytesIO
from PIL import Image

auth_bp = Blueprint('auth', __name__)

# Ruta para el registro de votantes
@auth_bp.route('/votante_register', methods=['GET', 'POST'])
def votante_register():
    if request.method == 'POST':
        name = request.form.get('name')
        photo_data_url = request.form.get('photo')

        try:
            # Decodificar la imagen base64
            header, encoded = photo_data_url.split(",", 1)
            image_data = base64.b64decode(encoded)
            image = Image.open(BytesIO(image_data))
            image_np = np.array(image)
            encodings = face_recognition.face_encodings(image_np)

            if len(encodings) == 0:
                flash("No se detectó ningún rostro.")
                return redirect(url_for('auth.votante_register'))

            # Crear un nuevo usuario
            nuevo_usuario = Usuario(
                nombre=name,
                face_encoding=encodings[0].tobytes(),
                password_hash=generate_password_hash("default_password")  # Contraseña por defecto
            )
            db.session.add(nuevo_usuario)
            db.session.commit()
            flash("Registro exitoso.")
            return redirect(url_for('auth.votante_login'))

        except Exception as e:
            flash("Error en el registro.")
            return redirect(url_for('auth.votante_register'))

    return render_template('user_register.html')

# Ruta para el login de votantes
@auth_bp.route('/votante_login', methods=['GET', 'POST'])
def votante_login():
    if request.method == 'POST':
        name = request.form.get('name')
        photo_data_url = request.form.get('photo')

        usuario = Usuario.query.filter_by(nombre=name).first()
        if not usuario:
            flash("Usuario no encontrado.")
            return redirect(url_for('auth.votante_login'))

        try:
            # Decodificar la imagen base64
            header, encoded = photo_data_url.split(",", 1)
            image_data = base64.b64decode(encoded)
            image = Image.open(BytesIO(image_data))
            image_np = np.array(image)
            login_encodings = face_recognition.face_encodings(image_np)

            if len(login_encodings) == 0:
                flash("No se detectó ningún rostro.")
                return redirect(url_for('auth.votante_login'))

            # Verificar si las caras coinciden
            match = face_recognition.compare_faces(
                [np.frombuffer(usuario.face_encoding, dtype=np.float64)],
                login_encodings[0]
            )[0]

            if match:
                session['usuario_id'] = usuario.id
                flash("Inicio de sesión exitoso.")
                return redirect(url_for('user.user_dashboard'))  # O la ruta correspondiente
            else:
                flash("Fallo en el reconocimiento facial.")
                return redirect(url_for('auth.votante_login'))

        except Exception as e:
            flash("Error en el inicio de sesión.")
            return redirect(url_for('auth.votante_login'))

    return render_template('user_login.html')

# Ruta para el login del administrador
@auth_bp.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        password = request.form.get('password')

        # Verificar que la contraseña sea la dirección del contrato (esto debe ser más seguro en la práctica)
        contract_address = '0xb5f62ce407dE0F56F1D5b319e3AF0e9aE2D2E991'  # Dirección del contrato
        if password == contract_address:
            session['admin'] = True
            flash("Inicio de sesión como administrador exitoso.")
            return redirect(url_for('admin.admin_dashboard'))  # O la ruta correspondiente
        else:
            flash("Contraseña incorrecta.")
            return redirect(url_for('auth.admin_login'))

    return render_template('admin_login.html')

# Ruta para el logout
@auth_bp.route('/logout')
def logout():
    session.clear()
    flash("Has cerrado sesión.")
    return redirect(url_for('auth.votante_login'))  # O la ruta inicial correspondiente
