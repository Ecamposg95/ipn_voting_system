from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from werkzeug.security import check_password_hash, generate_password_hash
from models import Usuario, db
import base64
from io import BytesIO
from PIL import Image
import face_recognition
import numpy as np

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/')
def index():
    # Página de selección de rol de usuario (Administrador o Votante)
    return render_template('index.html')

@auth_bp.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        password = request.form.get('password')
        
        # Verificación de usuario administrador
        usuario = Usuario.query.filter_by(nombre=nombre, es_admin=True).first()
        if usuario and check_password_hash(usuario.password_hash, password):
            session['usuario_id'] = usuario.id
            flash('Inicio de sesión exitoso como Administrador.')
            return redirect(url_for('admin.admin_dashboard'))
        else:
            flash('Credenciales de administrador incorrectas. Inténtalo de nuevo.')
            return redirect(url_for('auth.admin_login'))
    
    return render_template('admin_login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        data = request.get_json()
        name = data.get('name')
        photo_data_url = data.get('photo')

        if not name or not photo_data_url:
            return jsonify({"message": "Por favor, proporciona un nombre y una imagen."}), 400

        try:
            header, encoded = photo_data_url.split(",", 1)
            image_data = base64.b64decode(encoded)
            image = Image.open(BytesIO(image_data))
            image_np = np.array(image)

            # Extraer el encoding facial
            encodings = face_recognition.face_encodings(image_np)
            if len(encodings) == 0:
                return jsonify({"message": "No se detectó ningún rostro en la imagen. Inténtalo de nuevo."}), 400

            # Crear el usuario y guardar en la base de datos
            nuevo_usuario = Usuario(
                nombre=name,
                face_encoding=encodings[0].tobytes(),
                password_hash=generate_password_hash("optional_password")  # Contraseña opcional
            )
            db.session.add(nuevo_usuario)
            db.session.commit()
            
            return jsonify({"message": "Registro exitoso"}), 200
        except Exception as e:
            print(f"Error en el procesamiento de la imagen para el registro: {e}")
            return jsonify({"message": "Error en el registro. Inténtalo de nuevo."}), 500

    return render_template('user_register.html')

@auth_bp.route('/user_login', methods=['GET', 'POST'])
def user_login():
    if request.method == 'POST':
        data = request.get_json()
        nombre = data.get('name')
        photo_data_url = data.get('photo')
        
        usuario = Usuario.query.filter_by(nombre=nombre, es_admin=False).first()
        if not usuario:
            return jsonify({"success": False, "message": "Usuario no encontrado. Inténtalo de nuevo."}), 400

        try:
            header, encoded = photo_data_url.split(",", 1)
            image_data = base64.b64decode(encoded)
            image = Image.open(BytesIO(image_data))
            image_np = np.array(image)

            login_encodings = face_recognition.face_encodings(image_np)
            if len(login_encodings) == 0:
                return jsonify({"success": False, "message": "No se detectó ningún rostro. Inténtalo de nuevo."}), 400
            
            match = face_recognition.compare_faces(
                [np.frombuffer(usuario.face_encoding, dtype=np.float64)],
                login_encodings[0]
            )[0]
            if match:
                session['usuario_id'] = usuario.id
                return jsonify({"success": True}), 200
            else:
                return jsonify({"success": False, "message": "Reconocimiento facial fallido. Inténtalo de nuevo."}), 400

        except Exception as e:
            print(f"Error en el procesamiento de la imagen para inicio de sesión: {e}")
            return jsonify({"success": False, "message": "Error en el reconocimiento facial. Inténtalo de nuevo."}), 500

    return render_template('user_login.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('Has cerrado sesión exitosamente.')
    return redirect(url_for('auth.index'))