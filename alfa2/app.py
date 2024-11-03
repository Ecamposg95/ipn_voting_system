from flask import Flask, redirect, url_for
from config import Config
from models import db, Usuario
from auth_routes import auth_bp
from admin_routes import admin_bp
from user_routes import user_bp
from werkzeug.security import generate_password_hash

# Inicializar la aplicación Flask
app = Flask(__name__)
app.config.from_object(Config)

# Inicializar la base de datos
db.init_app(app)

# Registrar los Blueprints
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(admin_bp, url_prefix='/admin')
app.register_blueprint(user_bp, url_prefix='/user')

# Ruta de inicio
@app.route('/')
def home():
    return redirect(url_for('auth.index'))  # Redirigir a la página de inicio de autenticación

# Crear el usuario administrador por defecto si no existe
def crear_usuario_administrador():
    with app.app_context():
        admin = Usuario.query.filter_by(nombre="admin", es_admin=True).first()
        if not admin:
            admin = Usuario(
                nombre="admin",
                es_admin=True,
                password_hash=generate_password_hash("123456")
            )
            db.session.add(admin)
            db.session.commit()
            print("Usuario administrador creado con credenciales 'admin' y '123456'")
        else:
            print("Usuario administrador ya existe")

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Crear tablas si no existen
        crear_usuario_administrador()  # Crear el usuario administrador si no existe
    app.run(debug=True)
