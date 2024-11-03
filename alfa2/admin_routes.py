from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models import Votacion, OpcionVotacion, Usuario, db
from datetime import datetime
from functools import wraps

admin_bp = Blueprint('admin', __name__)

# Decorador para requerir que el usuario sea administrador
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        usuario_id = session.get('usuario_id')
        usuario = Usuario.query.get(usuario_id)
        if not usuario or not usuario.es_admin:
            flash('Acceso denegado. Se requieren privilegios de administrador.')
            return redirect(url_for('auth.index'))
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/dashboard')
@admin_required
def admin_dashboard():
    # Muestra el panel de administración
    return render_template('admin_dashboard.html')

@admin_bp.route('/crear_votacion', methods=['GET', 'POST'])
@admin_required
def crear_votacion():
    if request.method == 'POST':
        titulo = request.form['titulo']
        descripcion = request.form['descripcion']
        fecha_inicio_str = request.form['fecha_inicio']
        fecha_fin_str = request.form['fecha_fin']
        opciones = request.form.getlist('opciones[]')

        # Convertir fechas a objetos datetime
        try:
            fecha_inicio = datetime.strptime(fecha_inicio_str, '%Y-%m-%d')
            fecha_fin = datetime.strptime(fecha_fin_str, '%Y-%m-%d')
        except ValueError:
            flash("Formato de fecha inválido. Utiliza el formato YYYY-MM-DD.")
            return redirect(url_for('admin.crear_votacion'))

        if len(opciones) < 2 or len(opciones) > 6:
            flash('Debe ingresar entre 2 y 6 opciones.')
            return redirect(url_for('admin.crear_votacion'))

        nueva_votacion = Votacion(
            titulo=titulo,
            descripcion=descripcion,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            activa=True
        )
        db.session.add(nueva_votacion)
        db.session.commit()

        # Crear las opciones de votación
        for opcion_texto in opciones:
            opcion = OpcionVotacion(texto=opcion_texto, votacion_id=nueva_votacion.id)
            db.session.add(opcion)

        db.session.commit()
        flash('Votación creada exitosamente.')
        return redirect(url_for('admin.admin_dashboard'))
    
    return render_template('crear_votacion.html')

@admin_bp.route('/ver_votaciones')
@admin_required
def ver_votaciones():
    # Obtener todas las votaciones creadas
    votaciones = Votacion.query.all()
    return render_template('ver_votaciones.html', votaciones=votaciones)

@admin_bp.route('/resultados/<int:votacion_id>')
@admin_required
def resultados(votacion_id):
    # Muestra los resultados de una votación específica
    votacion = Votacion.query.get_or_404(votacion_id)
    resultados = []

    for opcion in votacion.opciones:
        # Usa len(opcion.votos) en lugar de count() para contar el número de votos
        votos_count = len(opcion.votos)
        resultados.append({
            'opcion': opcion.texto,
            'votos': votos_count
        })
    
    return render_template('resultados.html', votacion=votacion, resultados=resultados)

@admin_bp.route('/ver_usuarios')
@admin_required
def ver_usuarios():
    # Mostrar todos los usuarios registrados
    usuarios = Usuario.query.filter_by(es_admin=False).all()
    return render_template('ver_usuarios.html', usuarios=usuarios)
