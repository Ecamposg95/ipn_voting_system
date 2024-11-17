from flask import Blueprint, render_template, redirect, url_for, session, jsonify, request
from utils.auth import authenticate_admin, authenticate_user, logout_user, register_user
from models.voter_model import Voter, db

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/admin_login', methods=["GET", "POST"])
def admin_login():
    """Autentica al administrador y establece la sesión."""
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        
        # Autenticación del administrador
        if authenticate_admin(username, password):
            session["is_admin"] = True
            return redirect(url_for("admin.admin_dashboard"))
        return render_template("admin_login.html", error="Credenciales inválidas para el administrador.")
    
    # Renderizar el formulario de inicio de sesión del administrador
    return render_template("admin_login.html")

@auth_bp.route('/voter_login', methods=["GET", "POST"])
def voter_login():
    """Autentica al votante utilizando reconocimiento facial."""
    if request.method == "POST":
        data = request.get_json()
        name = data.get("name")
        photo = data.get("photo")
        
        # Validación de campos requeridos
        if not name or not photo:
            return jsonify({"success": False, "message": "Nombre y foto son obligatorios"}), 400
        
        # Autenticación mediante reconocimiento facial
        result = authenticate_user(name, photo)
        if result["success"]:
            session["authenticated"] = True
            session["voter_name"] = name
            # Agregar la dirección del votante a la sesión
            voter = Voter.query.filter_by(name=name).first()
            if voter:
                session["voter_address"] = voter.address
            return jsonify({"redirect": url_for("voter.voter_dashboard")})
        return jsonify(result), 401
    
    # Renderizar el formulario de inicio de sesión del votante
    return render_template("voter_login.html")


@auth_bp.route('/register', methods=["GET", "POST"])
def register():
    """Permite que los votantes se registren ellos mismos en el sistema."""
    if request.method == "POST":
        try:
            data = request.get_json() or request.form
            name = data.get("name")
            address = data.get("address")
            photo = data.get("photo")  # Imagen en formato base64

            # Validación de entrada
            if not name or not address or not photo:
                return jsonify({"error": "Nombre, dirección y foto son obligatorios"}), 400
            
            # Registrar usuario con reconocimiento facial
            result = register_user(name, photo)
            if "error" in result:
                return jsonify(result), 400
            
            # Guardar votante en la base de datos
            new_voter = Voter(name=name, address=address)
            db.session.add(new_voter)
            db.session.commit()
            return jsonify({"message": "Registro exitoso. Ahora puedes iniciar sesión."}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": f"Error en el registro: {str(e)}"}), 500

    # Renderizar el formulario de registro
    return render_template("register.html")

@auth_bp.route('/logout', methods=["GET", "POST"])
def logout():
    """Cierra la sesión del usuario y redirige a la página principal."""
    if request.method == "POST" or request.method == "GET":
        logout_user()
        return redirect(url_for("general.index"))
