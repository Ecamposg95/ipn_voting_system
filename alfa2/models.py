from flask_sqlalchemy import SQLAlchemy
from datetime import datetime  # Importación de datetime

db = SQLAlchemy()

class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(80), unique=True, nullable=False)
    es_admin = db.Column(db.Boolean, default=False)
    face_encoding = db.Column(db.LargeBinary)
    password_hash = db.Column(db.String(128))
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)  # Campo de fecha de registro
    votos = db.relationship('Voto', backref='votante', lazy=True)
    

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
    fecha = db.Column(db.DateTime, default=db.func.current_timestamp())  # Fecha y hora del voto
