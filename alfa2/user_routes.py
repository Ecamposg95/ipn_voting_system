from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models import Votacion, Voto, db

user_bp = Blueprint('user', __name__)

# Ruta para el dashboard del usuario
@user_bp.route('/dashboard')
def user_dashboard():
    # Verificar si el usuario ha iniciado sesión
    if 'usuario_id' not in session:
        flash('Por favor, inicia sesión.')
        return redirect(url_for('auth.user_login'))
    
    # Obtener las votaciones activas
    votaciones_activas = Votacion.query.filter_by(activa=True).all()
    return render_template('user_dashboard.html', votaciones=votaciones_activas)

# Ruta para votar en una votación específica
@user_bp.route('/votar/<int:votacion_id>', methods=['GET', 'POST'])
def votar(votacion_id):
    # Verificar si el usuario ha iniciado sesión
    if 'usuario_id' not in session:
        flash('Por favor, inicia sesión.')
        return redirect(url_for('auth.user_login'))
    
    votacion = Votacion.query.get_or_404(votacion_id)
    
    # Verificar si el usuario ya ha votado en esta votación
    voto_existente = Voto.query.filter_by(votacion_id=votacion_id, usuario_id=session['usuario_id']).first()
    if voto_existente:
        flash('Ya has votado en esta votación.')
        return redirect(url_for('user.user_dashboard'))
    
    if request.method == 'POST':
        opcion_id = request.form.get('opcion')
        if not opcion_id:
            flash('Por favor, selecciona una opción para votar.')
            return redirect(url_for('user.votar', votacion_id=votacion_id))
        
        # Registrar el voto
        voto = Voto(votacion_id=votacion_id, usuario_id=session['usuario_id'], opcion_id=opcion_id)
        db.session.add(voto)
        db.session.commit()
        
        flash('Voto registrado exitosamente.')
        return redirect(url_for('user.user_dashboard'))
    
    return render_template('votar.html', votacion=votacion)

# Ruta para cerrar sesión
@user_bp.route('/logout')
def logout():
    # Limpiar la sesión del usuario
    session.clear()
    flash('Has cerrado sesión exitosamente.')
    return redirect(url_for('auth.user_login'))
