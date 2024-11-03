from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models import Votacion, Voto, db

user_bp = Blueprint('user', __name__)

@user_bp.route('/dashboard')
def user_dashboard():
    votaciones_activas = Votacion.query.filter_by(activa=True).all()
    return render_template('user_dashboard.html', votaciones=votaciones_activas)

@user_bp.route('/votar/<int:votacion_id>', methods=['GET', 'POST'])
def votar(votacion_id):
    votacion = Votacion.query.get_or_404(votacion_id)
    if request.method == 'POST':
        opcion_id = request.form['opcion']
        voto = Voto(votacion_id=votacion_id, usuario_id=session['usuario_id'], opcion_id=opcion_id)
        db.session.add(voto)
        db.session.commit()
        flash('Voto registrado.')
        return redirect(url_for('user.user_dashboard'))
    
    return render_template('votar.html', votacion=votacion)
