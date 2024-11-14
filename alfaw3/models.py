from datetime import datetime
from . import db

class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(80), unique=True, nullable=False)
    face_encoding = db.Column(db.LargeBinary)
    es_admin = db.Column(db.Boolean, default=False)
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)

class Votacion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(200), nullable=False)
    descripcion = db.Column(db.Text)
    fecha_inicio = db.Column(db.DateTime, nullable=False)
    fecha_fin = db.Column(db.DateTime, nullable=False)
    opciones = db.relationship('OpcionVotacion', backref='votacion', lazy=True)

class OpcionVotacion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    texto = db.Column(db.String(200), nullable=False)
    votacion_id = db.Column(db.Integer, db.ForeignKey('votacion.id'), nullable=False)

class Voto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    votacion_id = db.Column(db.Integer, db.ForeignKey('votacion.id'), nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    opcion_id = db.Column(db.Integer, db.ForeignKey('opcion_votacion.id'), nullable=False)
    fecha = db.Column(db.DateTime, default=datetime.utcnow)
