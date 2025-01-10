from flask import Blueprint, render_template

# Define el blueprint
general_bp = Blueprint('general', __name__)

# Ruta para la página principal
@general_bp.route('/')
def index():
    return render_template("index.html")
