from flask import Flask, render_template, redirect, url_for, request, session, flash
from web3 import Web3
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = 'mysecret'

# Conectar a la blockchain (Ganache local)
w3 = Web3(Web3.HTTPProvider('http://127.0.0.1:7545'))
with open('VotingContract_abi.json', 'r') as abi_file:
    contract_abi = json.load(abi_file)
contract_address = '0xYourContractAddress'  # Reemplaza con la dirección de tu contrato
voting_contract = w3.eth.contract(address=contract_address, abi=contract_abi)

# Ruta principal
@app.route('/')
def home():
    return render_template('index.html')

# Ruta para desplegar el contrato
@app.route('/deploy', methods=['POST'])
def deploy_contract():
    # Desplegar el contrato si no está desplegado
    pass  # Lógica para desplegar el contrato

# Ruta de login para administrador
@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        admin_address = request.form['admin_address']
        # Verificar que la dirección del admin es válida
        if admin_address.lower() == w3.eth.accounts[0].lower():  # Suponiendo que la cuenta 0 es la del admin
            session['admin'] = True
            flash('Has iniciado sesión como Administrador', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Dirección incorrecta', 'danger')
    return render_template('admin_login.html')

# Ruta de login para votante
@app.route('/votante_login', methods=['GET', 'POST'])
def votante_login():
    if request.method == 'POST':
        voter_address = request.form['voter_address']
        # Verificar que el votante está registrado
        if not voting_contract.functions.voters(voter_address).call():
            flash('Este votante no está registrado', 'danger')
        else:
            session['voter'] = voter_address
            flash('Has iniciado sesión como Votante', 'success')
            return redirect(url_for('votante_dashboard'))
    return render_template('votante_login.html')

# Ruta para el registro del votante (usando reconocimiento facial en el frontend)
@app.route('/register_voter', methods=['GET', 'POST'])
def register_voter():
    if request.method == 'POST':
        voter_address = request.form['voter_address']
        # Registrar al votante en el contrato inteligente
        # Aquí puede ir la lógica del reconocimiento facial, luego registrar en el contrato
        tx_hash = voting_contract.functions.registerVoter(voter_address).transact({'from': w3.eth.accounts[0]})
        w3.eth.wait_for_transaction_receipt(tx_hash)
        flash('Votante registrado exitosamente', 'success')
        return redirect(url_for('votante_login'))
    return render_template('user_register.html')

# Ruta para crear votaciones (Administrador)
@app.route('/create_voting', methods=['GET', 'POST'])
def create_voting():
    if not session.get('admin'):
        return redirect(url_for('admin_login'))
    
    if request.method == 'POST':
        candidate_name = request.form['candidate_name']
        tx_hash = voting_contract.functions.addCandidate(candidate_name).transact({'from': w3.eth.accounts[0]})
        w3.eth.wait_for_transaction_receipt(tx_hash)
        flash(f'El candidato {candidate_name} ha sido añadido a la votación', 'success')
    return render_template('create_voting.html')

# Ruta para votar
@app.route('/vote', methods=['GET', 'POST'])
def vote():
    if not session.get('voter'):
        return redirect(url_for('votante_login'))

    if request.method == 'POST':
        candidate_id = int(request.form['candidate_id'])
        tx_hash = voting_contract.functions.vote(candidate_id).transact({'from': session['voter']})
        w3.eth.wait_for_transaction_receipt(tx_hash)
        flash(f'Has votado por el candidato con ID {candidate_id}', 'success')
        return redirect(url_for('results'))
    return render_template('votar.html')

# Ruta para ver los resultados
@app.route('/results')
def results():
    winner = voting_contract.functions.getWinner().call()
    return render_template('results.html', winner=winner)

# Dashboard del administrador (ver resultados)
@app.route('/admin_dashboard')
def admin_dashboard():
    if not session.get('admin'):
        return redirect(url_for('admin_login'))
    
    total_votes = voting_contract.functions.totalVotes().call()
    candidates = []
    for i in range(1, voting_contract.functions.candidatesCount().call() + 1):
        candidate = voting_contract.functions.candidates(i).call()
        candidates.append(candidate)
    return render_template('admin_dashboard.html', total_votes=total_votes, candidates=candidates)

# Dashboard del votante (ver resultados)
@app.route('/votante_dashboard')
def votante_dashboard():
    if not session.get('voter'):
        return redirect(url_for('votante_login'))
    
    return render_template('votante_dashboard.html')

if __name__ == '__main__':
    app.run(debug=True)
