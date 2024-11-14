from flask import Blueprint, render_template, request
from .models import Votacion, OpcionVotacion, db

user_bp = Blueprint('user', __name__)

@user_bp.route('/dashboard')
def user_dashboard():
    votaciones = Votacion.query.all()
    return render_template('votar.html', votaciones=votaciones)

@user_bp.route('/votar/<int:votacion_id>', methods=['GET', 'POST'])
def votar(votacion_id):
    votacion = Votacion.query.get_or_404(votacion_id)
    if request.method == 'POST':
        opcion_id = request.form.get('opcion')
        voto = Voto(usuario_id=session['usuario_id'], votacion_id=votacion_id, opcion_id=opcion_id)
        db.session.add(voto)
        db.session.commit()
        flash("Voto registrado con éxito.")
        return redirect(url_for('user.user_dashboard'))
    
    opciones = OpcionVotacion.query.filter_by(votacion_id=votacion_id).all()
    return render_template('votar.html', votacion=votacion, opciones=opciones)
