from flask import Flask
from utils.config import DevelopmentConfig
from models import db  # Asegúrate de que estás importando db de models/__init__.py
from routes.admin_routes import admin_bp
from routes.auth_routes import auth_bp
from routes.general_routes import general_bp
from routes.voter_routes import voter_bp
from utils.blockchain import BlockchainHandler
from utils.whitelist_loader import load_whitelist

def create_app():
    # Crear la aplicación Flask
    app = Flask(__name__)
    app.config.from_object(DevelopmentConfig)

    # Inicializar la base de datos
    db.init_app(app)  # Esto asegura que SQLAlchemy se registre con la instancia app

    # Inicializar el manejador de blockchain
    blockchain = BlockchainHandler()

    with app.app_context():
        # Crear las tablas de la base de datos
        db.create_all()
        # Cargar la lista blanca en el contrato inteligente
        load_whitelist(blockchain)

    # Registrar los blueprints para una arquitectura modular
    register_blueprints(app)

    return app

def register_blueprints(app):
    """Registrar blueprints para rutas modulares."""
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(general_bp)
    app.register_blueprint(voter_bp, url_prefix='/voter')

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
