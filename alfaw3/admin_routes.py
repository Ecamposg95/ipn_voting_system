from flask import Blueprint, render_template, request
from .models import Votacion, OpcionVotacion, db

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/create_votacion', methods=['GET', 'POST'])
def create_votacion():
    if request.method == 'POST':
        titulo = request.form.get('titulo')
        descripcion = request.form.get('descripcion')
        fecha_inicio = request.form.get('fecha_inicio')
        fecha_fin = request.form.get('fecha_fin')

        votacion = Votacion(titulo=titulo, descripcion=descripcion, fecha_inicio=fecha_inicio, fecha_fin=fecha_fin)
        db.session.add(votacion)
        db.session.commit()
        flash("Votación creada con éxito.")
        return redirect(url_for('admin.create_votacion'))

    return render_template('create_votacion.html')
