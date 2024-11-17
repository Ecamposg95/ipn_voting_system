from flask import Blueprint, render_template, redirect, url_for, session, jsonify, request
from utils.blockchain import BlockchainHandler
from models.voter_model import Voter, db

admin_bp = Blueprint('admin', __name__)
blockchain = BlockchainHandler()

@admin_bp.route('/')
def admin_dashboard():
    """Renderiza el panel de administración, mostrando la lista de votantes."""
    if not session.get("is_admin"):
        return redirect(url_for("auth.admin_login"))
    votantes = Voter.query.all()
    return render_template("admin_dashboard.html", votantes=votantes)

@admin_bp.route('/end_voting', methods=["POST"])
def end_voting():
    """Finaliza la votación en la blockchain."""
    if not session.get("is_admin"):
        return redirect(url_for("auth.admin_login"))
    try:
        blockchain.contract.functions.endVoting().transact({'from': blockchain.w3.eth.accounts[0]})
        return jsonify({"message": "Votación finalizada exitosamente."}), 200
    except Exception as e:
        return jsonify({"error": f"Error al finalizar la votación: {str(e)}"}), 500

@admin_bp.route('/view_voters', methods=["GET"])
def view_voters():
    """Muestra la lista de votantes registrados."""
    if not session.get("is_admin"):
        return redirect(url_for("auth.admin_login"))
    votantes = Voter.query.all()
    return render_template("view_voters.html", votantes=votantes)

@admin_bp.route('/register_voter', methods=["GET", "POST"])
def register_voter():
    """Registra un nuevo votante en la base de datos con captura facial, realizado por el administrador."""
    if not session.get("is_admin"):
        return redirect(url_for("auth.admin_login"))
    
    if request.method == "POST":
        data = request.get_json() or request.form
        name = data.get("name")
        address = data.get("address")
        photo = data.get("photo")  # Imagen en formato base64

        if not name or not address or not photo:
            return jsonify({"error": "Nombre, dirección y foto son obligatorios"}), 400
        
        try:
            new_voter = Voter(name=name, address=address)
            db.session.add(new_voter)
            db.session.commit()
            
            blockchain.contract.functions.addVoterToWhitelist(address).transact({'from': blockchain.w3.eth.accounts[0]})
            
            return jsonify({"message": "Votante registrado exitosamente."}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": f"Error al registrar el votante: {str(e)}"}), 500

    return render_template("register_voter_admin.html")

@admin_bp.route('/view_results', methods=["GET"])
def view_results():
    """Muestra los resultados de la votación."""
    if not session.get("is_admin"):
        return redirect(url_for("auth.admin_login"))
    
    try:
        # Usar el getter de Solidity para obtener totalVotes
        total_votes = blockchain.contract.functions.totalVotes().call()
        return render_template("results.html", total_votes=total_votes)
    except Exception as e:
        print(f"Error al obtener los resultados: {e}")  # Log de error en la terminal
        return render_template("results.html", error="No se pudieron cargar los resultados."), 500

