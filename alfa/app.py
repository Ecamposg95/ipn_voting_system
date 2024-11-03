import os
import datetime
import base64
import numpy as np
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import face_recognition
from io import BytesIO
from PIL import Image
from functools import wraps

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key_here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///voting_system.db'
app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(), 'static', 'uploads')
db = SQLAlchemy(app)

# Modelos de Base de Datos
class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(80), unique=True, nullable=False)
    es_admin = db.Column(db.Boolean, default=False)
    face_encoding = db.Column(db.LargeBinary)
    password_hash = db.Column(db.String(128))
    votos = db.relationship('Voto', backref='votante', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Votacion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(200), nullable=False)
    descripcion = db.Column(db.Text)
    fecha_inicio = db.Column(db.DateTime, nullable=False)
    fecha_fin = db.Column(db.DateTime, nullable=False)
    opciones = db.relationship('OpcionVotacion', backref='votacion', lazy=True)
    activa = db.Column(db.Boolean, default=True)

class OpcionVotacion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    texto = db.Column(db.String(200), nullable=False)
    votacion_id = db.Column(db.Integer, db.ForeignKey('votacion.id'), nullable=False)
    votos = db.relationship('Voto', backref='opcion', lazy=True)

class Voto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    votacion_id = db.Column(db.Integer, db.ForeignKey('votacion.id'), nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    opcion_id = db.Column(db.Integer, db.ForeignKey('opcion_votacion.id'), nullable=False)
    fecha = db.Column(db.DateTime, default=datetime.datetime.utcnow)

# Funciones auxiliares para el manejo de imágenes y autenticación
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
        if not os.path.exists(app.config['UPLOAD_FOLDER']):
            os.makedirs(app.config['UPLOAD_FOLDER'])
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        image.save(filepath)
        return filepath
    except Exception as e:
        print(f"Error saving image: {e}")
        return None

# Decoradores para proteger rutas
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'usuario_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'usuario_id' not in session:
            return redirect(url_for('login'))
        usuario = Usuario.query.get(session['usuario_id'])
        if not usuario or not usuario.es_admin:
            flash('Acceso denegado. Se requieren privilegios de administrador.')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

# Rutas de la aplicación
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        password = request.form.get('password')  # Contraseña opcional
        photo_data_url = request.form.get('photo')  # Imagen obligatoria

        if not nombre or not photo_data_url:
            flash('Por favor, complete todos los campos requeridos.')
            return redirect(url_for('registro'))

        if Usuario.query.filter_by(nombre=nombre).first():
            flash('El nombre de usuario ya está en uso.')
            return redirect(url_for('registro'))
        
        nuevo_usuario = Usuario(nombre=nombre)

        # Solo establece la contraseña si el usuario ingresó una
        if password:
            nuevo_usuario.set_password(password)

        # Procesar y guardar la imagen facial
        image = decode_image(photo_data_url)
        if image:
            filename = f"{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}_{nombre}.jpg"
            filepath = save_image(image, filename)
            if filepath:
                face_image = face_recognition.load_image_file(filepath)
                face_encodings = face_recognition.face_encodings(face_image)
                if face_encodings:
                    nuevo_usuario.face_encoding = face_encodings[0].tobytes()
                else:
                    flash('No se pudo detectar un rostro en la imagen proporcionada.')
                    return redirect(url_for('registro'))
            else:
                flash('Error al guardar la imagen.')
                return redirect(url_for('registro'))
        else:
            flash('Error al procesar la imagen. Asegúrese de que es una imagen válida.')
            return redirect(url_for('registro'))

        db.session.add(nuevo_usuario)
        db.session.commit()
        
        session['usuario_id'] = nuevo_usuario.id
        return redirect(url_for('user_dashboard'))
        
    return render_template('registro.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        password = request.form.get('password')
        
        usuario = Usuario.query.filter_by(nombre=nombre).first()
        if usuario and (password and usuario.check_password(password) or not password):
            session['usuario_id'] = usuario.id
            if usuario.es_admin:
                return redirect(url_for('admin_dashboard'))
            else:
                return redirect(url_for('user_dashboard'))
        else:
            flash('Credenciales incorrectas. Inténtalo de nuevo.')
    return render_template('login.html')

@app.route('/user_dashboard')
@login_required
def user_dashboard():
    votaciones_activas = Votacion.query.filter_by(activa=True).all()
    return render_template('user_dashboard.html', votaciones=votaciones_activas)

@app.route('/votar/<int:votacion_id>', methods=['GET', 'POST'])
@login_required
def votar(votacion_id):
    votacion = Votacion.query.get_or_404(votacion_id)
    
    if not votacion.activa:
        flash('Esta votación ya no está activa')
        return redirect(url_for('user_dashboard'))
        
    if Voto.query.filter_by(votacion_id=votacion_id, usuario_id=session['usuario_id']).first():
        flash('Ya has votado en esta votación')
        return redirect(url_for('user_dashboard'))
    
    if request.method == 'POST':
        opcion_id = request.form['opcion']
        nuevo_voto = Voto(
            votacion_id=votacion_id,
            usuario_id=session['usuario_id'],
            opcion_id=opcion_id
        )
        db.session.add(nuevo_voto)
        db.session.commit()
        
        flash('Voto registrado exitosamente')
        return redirect(url_for('user_dashboard'))
    
    return render_template('votar.html', votacion=votacion)

@app.route('/admin_dashboard')
@admin_required
def admin_dashboard():
    return render_template('admin_dashboard.html')

@app.route('/admin/crear_votacion', methods=['GET', 'POST'])
@admin_required
def crear_votacion():
    if request.method == 'POST':
        titulo = request.form['titulo']
        descripcion = request.form['descripcion']
        fecha_inicio = request.form['fecha_inicio']
        fecha_fin = request.form['fecha_fin']
        opciones = request.form.getlist('opciones[]')  # Lista de opciones

        # Validar que haya entre 2 y 6 opciones
        if len(opciones) < 2 or len(opciones) > 6:
            flash('Debe ingresar entre 2 y 6 opciones para la votación.')
            return redirect(url_for('crear_votacion'))

        nueva_votacion = Votacion(
            titulo=titulo,
            descripcion=descripcion,
            fecha_inicio=datetime.datetime.strptime(fecha_inicio, '%Y-%m-%d'),
            fecha_fin=datetime.datetime.strptime(fecha_fin, '%Y-%m-%d')
        )
        db.session.add(nueva_votacion)
        db.session.commit()
        
        for opcion in opciones:
            nueva_opcion = OpcionVotacion(texto=opcion, votacion_id=nueva_votacion.id)
            db.session.add(nueva_opcion)
        
        db.session.commit()
        flash('Votación creada exitosamente')
        return redirect(url_for('admin_dashboard'))
    
    return render_template('crear_votacion.html')

@app.route('/admin/ver_registros')
@admin_required
def ver_registros():
    usuarios = Usuario.query.all()
    return render_template('ver_registros.html', usuarios=usuarios)

@app.route('/admin/resultados/<int:votacion_id>')
@admin_required
def resultados(votacion_id):
    votacion = Votacion.query.get_or_404(votacion_id)
    resultados = []
    
    for opcion in votacion.opciones:
        votos_count = Voto.query.filter_by(opcion_id=opcion.id).count()
        resultados.append({
            'opcion': opcion.texto,
            'votos': votos_count
        })
    
    return render_template('resultados.html', votacion=votacion, resultados=resultados)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        # Crear usuario admin si no existe
        admin = Usuario.query.filter_by(nombre='admin').first()
        if not admin:
            admin = Usuario(nombre='admin', es_admin=True)
            admin.set_password('123456')
            db.session.add(admin)
            db.session.commit()
    
    app.run(debug=True)
