from flask import Blueprint, render_template, redirect, url_for, session, jsonify, request
from utils.blockchain import BlockchainHandler
from models.voter_model import Voter

voter_bp = Blueprint('voter', __name__)
blockchain = BlockchainHandler()

@voter_bp.route('/dashboard')
def voter_dashboard():
    if not session.get("authenticated"):
        return redirect(url_for("auth.voter_login"))
    voting_active = blockchain.contract.functions.isVotingActive().call()  # Ejemplo de llamada para saber si la votación está activa
    return render_template("voter_dashboard.html", voting_active=voting_active)

@voter_bp.route('/vote', methods=["GET", "POST"])
def cast_vote():
    if not session.get("authenticated"):
        return redirect(url_for("auth.voter_login"))

    if request.method == "POST":
        vote_option = request.form.get("vote_option")
        voter_address = session.get("voter_address")
        
        if not vote_option:
            return jsonify({"error": "Debe seleccionar una opción para votar."}), 400
        
        try:
            # Registrar el voto en la blockchain
            tx_hash = blockchain.contract.functions.castVote(vote_option).transact({'from': voter_address})
            blockchain.w3.eth.wait_for_transaction_receipt(tx_hash)
            return jsonify({"message": "Voto registrado exitosamente."}), 200
        except Exception as e:
            return jsonify({"error": f"Error al registrar el voto: {str(e)}"}), 500
    
    return render_template("vote.html")

@voter_bp.route('/results')
def view_results():
    if not session.get("authenticated"):
        return redirect(url_for("auth.voter_login"))
    
    # Lógica para obtener resultados de la votación
    total_votes = blockchain.contract.functions.getTotalVotes().call()
    return render_template("results.html", total_votes=total_votes)
