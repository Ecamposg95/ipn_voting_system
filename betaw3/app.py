from flask import Flask, render_template, redirect, url_for, request, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from utils.blockchain import BlockchainHandler
from utils.auth import authenticate_admin, authenticate_user, logout_user, register_user
import json
import os

app = Flask(__name__)
app.config.from_object('utils.config.DevelopmentConfig')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///voters.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
blockchain = BlockchainHandler()

# Modelo de Votante
class Voter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    address = db.Column(db.String(100), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)  # Para distinguir entre administrador y votante

# Inicializar la base de datos
with app.app_context():
    db.create_all()

# Cargar direcciones de la lista blanca desde el archivo JSON
def load_whitelist():
    try:
        with open('whitelist.json') as f:
            data = json.load(f)
            for address in data["addresses"]:
                # Registrar en el contrato inteligente
                tx_hash = blockchain.contract.functions.addVoterToWhitelist(address).transact({'from': blockchain.w3.eth.accounts[0]})
                blockchain.w3.eth.wait_for_transaction_receipt(tx_hash)
                print(f"Dirección {address} agregada a la lista blanca.")
    except Exception as e:
        print(f"Error al cargar la lista blanca: {e}")

# Ejecutar carga de lista blanca al iniciar la aplicación
with app.app_context():
    load_whitelist()

# Función para agregar un nuevo votante
def add_voter(name, address, is_admin=False):
    new_voter = Voter(name=name, address=address, is_admin=is_admin)
    db.session.add(new_voter)
    db.session.commit()
    if not is_admin:
        tx_hash = blockchain.contract.functions.addVoterToWhitelist(address).transact({'from': blockchain.w3.eth.accounts[0]})
        blockchain.w3.eth.wait_for_transaction_receipt(tx_hash)
        print(f"Votante {name} con dirección {address} añadido a la lista blanca.")

# Función para obtener todos los votantes
def get_all_voters():
    return Voter.query.all()

@app.route("/")
def index():
    return render_template("index.html")

# Ruta de inicio de sesión para el administrador
@app.route("/admin_login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        
        if authenticate_admin(username, password):
            session["is_admin"] = True
            return redirect(url_for("admin"))
        else:
            return "Credenciales inválidas para el administrador.", 401
    return render_template("admin_login.html")

# Ruta de inicio de sesión para el votante mediante reconocimiento facial
@app.route("/votante_login", methods=["GET", "POST"])
def votante_login():
    if request.method == "POST":
        data = request.get_json()
        name = data.get("name")
        photo = data.get("photo")
        
        result = authenticate_user(name, photo)
        if result["success"]:
            session["authenticated"] = True
            session["voter_name"] = name
            return jsonify({"redirect": url_for("vote")})
        return jsonify(result), 401
    return render_template("votante_login.html")

# Ruta de registro para votantes
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")
    elif request.method == "POST":
        data = request.get_json()
        name = data.get("name")
        photo = data.get("photo")
        address = data.get("address")

        if not address:
            return jsonify({"message": "La dirección es obligatoria"}), 400

        result = register_user(name, photo)
        if result["message"] == "Registro exitoso":
            add_voter(name, address)
            return jsonify({"redirect": url_for("vote")})
        return jsonify(result), 401

@app.route("/logout", methods=["GET", "POST"])
def logout():
    logout_user()
    return redirect(url_for("index"))


@app.route("/vote")
def vote():
    if "authenticated" not in session:
        return redirect(url_for("votante_login"))
    return render_template("vote.html")

@app.route("/admin")
def admin():
    if not session.get("is_admin"):
        return redirect(url_for("admin_login"))
    
    votantes = get_all_voters()
    return render_template("admin_dashboard.html", votantes=votantes)

# Ruta para finalizar la votación (solo para administrador)
@app.route("/end_voting", methods=["POST"])
def end_voting():
    if not session.get("is_admin"):
        return redirect(url_for("admin_login"))
    try:
        blockchain.contract.functions.endVoting().transact({'from': blockchain.w3.eth.accounts[0]})
        return jsonify({"message": "Votación finalizada exitosamente."}), 200
    except Exception as e:
        print(f"Error al finalizar la votación: {e}")
        return jsonify({"error": f"Error al finalizar la votación: {e}"}), 500


@app.route("/cast_vote", methods=["POST"])
def cast_vote():
    if "authenticated" not in session:
        return redirect(url_for("votante_login"))
    
    voter_name = session.get("voter_name")
    voter = Voter.query.filter_by(name=voter_name).first()
    
    if not voter or voter.is_admin:
        return "No tiene permisos para votar.", 403

    try:
        is_whitelisted = blockchain.contract.functions.whitelistedVoters(voter.address).call()
        print(f"Estado de habilitación en contrato para {voter.address}: {is_whitelisted}")

        if not is_whitelisted:
            return "Error: Usted no está habilitado para votar.", 403

        tx_hash = blockchain.contract.functions.castVote().transact({'from': voter.address})
        blockchain.w3.eth.wait_for_transaction_receipt(tx_hash)
        return "Voto registrado exitosamente."

    except Exception as e:
        print(f"Error al verificar el estado del votante o al registrar el voto: {e}")
        return f"Error al registrar el voto: {e}", 500

# Ruta para ver los votantes en una página HTML
@app.route("/view_voters_page")
def view_voters_page():
    if not session.get("is_admin"):
        return redirect(url_for("admin_login"))
    
    votantes = get_all_voters()
    return render_template("view_voters.html", votantes=votantes)

if __name__ == "__main__":
    app.run(debug=True)
