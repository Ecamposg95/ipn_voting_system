from flask import Flask, render_template, redirect, url_for, request, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from web3 import Web3 
from utils.blockchain import BlockchainHandler
from utils.auth import authenticate_admin, authenticate_user, logout_user, register_user
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
    enabled = db.Column(db.Boolean, default=False)

# Inicializar la base de datos
with app.app_context():
    db.create_all()

# Función para agregar un nuevo votante
def add_voter(name, address):
    new_voter = Voter(name=name, address=address)
    db.session.add(new_voter)
    db.session.commit()

# Función para obtener todos los votantes
def get_all_voters():
    return Voter.query.all()

# Función para obtener la dirección de un votante por su ID
def get_voter_address(voter_id):
    voter = Voter.query.get(voter_id)
    return voter.address if voter else None

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
        
        result = register_user(name, photo)
        if result["message"] == "Registro exitoso":
            # Generar una dirección hexadecimal de ejemplo y convertirla a formato checksum
            raw_address = "0x" + os.urandom(20).hex()  # Dirección de 40 caracteres en hexadecimal
            address = Web3.to_checksum_address(raw_address)  # Convertir a checksum
            add_voter(name, address)
            return jsonify({"redirect": url_for("vote")})
        return jsonify(result), 401

@app.route("/logout")
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

# Ruta para habilitar votantes en el contrato inteligente
@app.route("/enable_voter", methods=["POST"])
def enable_voter():
    if not session.get("is_admin"):
        return redirect(url_for("admin_login"))

    data = request.get_json()
    voter_id = data.get("voter_id")
    print(f"Voter ID received: {voter_id}")

    if voter_id is None:
        return jsonify({"error": "Voter ID is missing in the request."}), 400
    
    voter_address = get_voter_address(voter_id)
    print(f"Voter Address found: {voter_address}")

    if voter_address is None:
        return jsonify({"error": "Voter not found."}), 404

    try:
        # Habilitar al votante en el contrato inteligente
        tx_hash = blockchain.contract.functions.registerVoter(voter_address).transact({'from': blockchain.w3.eth.accounts[0]})
        print(f"Transaction hash: {tx_hash}")

        # Actualizar el estado de habilitación en la base de datos
        voter = Voter.query.get(voter_id)
        voter.enabled = True
        db.session.commit()
        return jsonify({"message": "Votante habilitado para votar."})
    except Exception as e:
        print(f"Error al habilitar el votante: {e}")
        return jsonify({"error": f"Error al habilitar el votante: {e}"}), 500

@app.route("/end_voting")
def end_voting():
    if not session.get("is_admin"):
        return redirect(url_for("admin_login"))
    blockchain.contract.functions.endVoting().transact({'from': blockchain.w3.eth.accounts[0]})
    return "Votación finalizada exitosamente."

@app.route("/view_results")
def view_results():
    if not session.get("is_admin"):
        return redirect(url_for("admin_login"))
    return "Resultados de la votación (en construcción)"

@app.route("/cast_vote", methods=["POST"])
def cast_vote():
    if "authenticated" not in session:
        return redirect(url_for("votante_login"))
    
    vote_option = request.form.get("vote_option")
    try:
        blockchain.cast_vote()
        return "Voto registrado exitosamente."
    except Exception as e:
        return f"Error al registrar el voto: {e}", 500

# Ruta para ver los votantes en formato JSON
@app.route("/view_voters")
def view_voters():
    if not session.get("is_admin"):
        return redirect(url_for("admin_login"))
    
    voters = [{"id": v.id, "name": v.name, "address": v.address, "enabled": v.enabled} for v in get_all_voters()]
    return jsonify(voters)

# Ruta para ver los votantes en una página HTML
@app.route("/view_voters_page")
def view_voters_page():
    if not session.get("is_admin"):
        return redirect(url_for("admin_login"))
    
    votantes = get_all_voters()
    return render_template("view_voters.html", votantes=votantes)

if __name__ == "__main__":
    app.run(debug=True)
