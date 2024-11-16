from flask import Blueprint, render_template, redirect, url_for, session, jsonify, request
from utils.blockchain import BlockchainHandler
from models.voter_model import Voter

voter_bp = Blueprint('voter', __name__)
blockchain = BlockchainHandler()

@voter_bp.route('/dashboard')
def voter_dashboard():
    """Renderiza el panel de votantes, verificando si la votación está activa."""
    if not session.get("authenticated"):
        return redirect(url_for("auth.voter_login"))
    
    try:
        # Llamar a la nueva función getVotingStatus en lugar de isVotingActive
        voting_active = blockchain.contract.functions.getVotingStatus().call()
        return render_template("voter_dashboard.html", voting_active=voting_active)
    except Exception as e:
        print(f"Error al obtener el estado de votación: {e}")
        return render_template("voter_dashboard.html", error="No se pudo cargar el estado de la votación.")

@voter_bp.route('/vote', methods=["GET", "POST"])
def cast_vote():
    """Permite al votante emitir su voto en la blockchain."""
    if not session.get("authenticated"):
        return redirect(url_for("auth.voter_login"))

    if request.method == "POST":
        vote_option = request.form.get("vote_option")
        voter_address = session.get("voter_address")
        
        if not vote_option:
            return jsonify({"error": "Debe seleccionar una opción para votar."}), 400
        
        try:
            # Registrar el voto en la blockchain
            tx_hash = blockchain.contract.functions.castVote().transact({'from': voter_address})
            blockchain.w3.eth.wait_for_transaction_receipt(tx_hash)
            return jsonify({"message": "Voto registrado exitosamente."}), 200
        except Exception as e:
            print(f"Error al registrar el voto: {e}")
            return jsonify({"error": f"Error al registrar el voto: {str(e)}"}), 500
    
    # Renderiza la página de votación
    return render_template("vote.html")

@voter_bp.route('/results')
def view_results():
    """Muestra los resultados de la votación."""
    if not session.get("authenticated"):
        return redirect(url_for("auth.voter_login"))
    
    try:
        # Obtener el total de votos desde la blockchain
        total_votes = blockchain.contract.functions.totalVotes().call()
        return render_template("results.html", total_votes=total_votes)
    except Exception as e:
        print(f"Error al obtener los resultados: {e}")
        return render_template("results.html", error="No se pudieron cargar los resultados.")
