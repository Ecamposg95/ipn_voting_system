import os
import datetime
import base64
import numpy as np
from flask import Flask, jsonify, request, render_template, redirect, url_for
import face_recognition
from io import BytesIO
from PIL import Image
import sqlite3

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(), 'static', 'uploads', 'images')
DATABASE = 'database.db'

# Inicializar la base de datos
def init_db():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY, name TEXT, encoding BLOB)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS publications
                 (id INTEGER PRIMARY KEY, title TEXT, author TEXT, year INTEGER, category TEXT)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS investigations
                 (id INTEGER PRIMARY KEY, title TEXT, researcher TEXT, year INTEGER, area TEXT)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS books
                 (id INTEGER PRIMARY KEY, title TEXT, author TEXT, year INTEGER, publisher TEXT)''')
    
    conn.commit()
    conn.close()

# Ejecutar la inicialización de la base de datos
init_db()

# Funciones de ayuda para la autenticación biométrica
def decode_image(data_url):
    try:
        header, encoded = data_url.split(",", 1)
        data = base64.b64decode(encoded)
        image = Image.open(BytesIO(data))
        return image
    except Exception as e:
        print(f"Error decoding image: {e}")
        return None

def save_image(image, filename):
    try:
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        image.save(filepath)
        return filepath
    except Exception as e:
        print(f"Error saving image: {e}")
        return None

def save_encoding(name, encoding):
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("INSERT INTO users (name, encoding) VALUES (?, ?)", (name, encoding.tobytes()))
    conn.commit()
    conn.close()

def load_encodings():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("SELECT name, encoding FROM users")
    users = c.fetchall()
    conn.close()
    return {name: np.frombuffer(enc, dtype=np.float64) for name, enc in users}

# Rutas para la autenticación biométrica
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    name = data.get('name')
    photo_data_url = data.get('photo')
    if photo_data_url and name:
        if not os.path.exists(app.config['UPLOAD_FOLDER']):
            os.makedirs(app.config['UPLOAD_FOLDER'])

        image = decode_image(photo_data_url)
        if image:
            filename = f"{datetime.date.today()}_{name}.jpg"
            filepath = save_image(image, filename)
            if filepath:
                encoding = face_recognition.face_encodings(face_recognition.load_image_file(filepath))
                if encoding:
                    save_encoding(name, encoding[0])
                    return jsonify({"message": "Registro exitoso"}), 200
    return jsonify({"message": "Error en el registro"}), 400

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    photo_data_url = data.get('photo')
    if photo_data_url:
        if not os.path.exists(app.config['UPLOAD_FOLDER']):
            os.makedirs(app.config['UPLOAD_FOLDER'])

        image = decode_image(photo_data_url)
        if image:
            login_filename = os.path.join(app.config['UPLOAD_FOLDER'], "login_face.jpg")
            image.save(login_filename)

            login_image = face_recognition.load_image_file(login_filename)
            login_face_encodings = face_recognition.face_encodings(login_image)

            if len(login_face_encodings) > 0:
                login_face_encoding = login_face_encodings[0]
                registered_data = load_encodings()
                for name, registered_face_encoding in registered_data.items():
                    matches = face_recognition.compare_faces([registered_face_encoding], login_face_encoding)
                    if any(matches):
                        return jsonify({"success": True, "name": name})

        return jsonify({"success": False})
    return redirect(request.url)

# Rutas CRUD para publicaciones
@app.route('/publications')
def list_publications():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("SELECT * FROM publications")
    records = c.fetchall()
    conn.close()
    return render_template('list_publications.html', records=records)

@app.route('/create/publication', methods=['GET', 'POST'])
def create_publication():
    if request.method == 'POST':
        title = request.form['title']
        author = request.form['author']
        year = request.form['year']
        category = request.form['category']
        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()
        c.execute("INSERT INTO publications (title, author, year, category) VALUES (?, ?, ?, ?)", (title, author, year, category))
        conn.commit()
        conn.close()
        return redirect(url_for('list_publications'))
    return render_template('create_publication.html')

@app.route('/edit/publication/<int:id>', methods=['GET', 'POST'])
def edit_publication(id):
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("SELECT * FROM publications WHERE id=?", (id,))
    record = c.fetchone()
    if request.method == 'POST':
        title = request.form['title']
        author = request.form['author']
        year = request.form['year']
        category = request.form['category']
        c.execute("UPDATE publications SET title=?, author=?, year=?, category=? WHERE id=?", (title, author, year, category, id))
        conn.commit()
        conn.close()
        return redirect(url_for('list_publications'))
    conn.close()
    return render_template('edit_publication.html', record=record)

@app.route('/delete/publication/<int:id>')
def delete_publication(id):
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("DELETE FROM publications WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('list_publications'))

# Repetir las rutas CRUD para investigaciones y libros
@app.route('/investigations')
def list_investigations():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("SELECT * FROM investigations")
    records = c.fetchall()
    conn.close()
    return render_template('list_investigations.html', records=records)

@app.route('/create/investigation', methods=['GET', 'POST'])
def create_investigation():
    if request.method == 'POST':
        title = request.form['title']
        researcher = request.form['researcher']
        year = request.form['year']
        area = request.form['area']
        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()
        c.execute("INSERT INTO investigations (title, researcher, year, area) VALUES (?, ?, ?, ?)", (title, researcher, year, area))
        conn.commit()
        conn.close()
        return redirect(url_for('list_investigations'))
    return render_template('create_investigation.html')

@app.route('/edit/investigation/<int:id>', methods=['GET', 'POST'])
def edit_investigation(id):
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("SELECT * FROM investigations WHERE id=?", (id,))
    record = c.fetchone()
    if request.method == 'POST':
        title = request.form['title']
        researcher = request.form['researcher']
        year = request.form['year']
        area = request.form['area']
        c.execute("UPDATE investigations SET title=?, researcher=?, year=?, area=? WHERE id=?", (title, researcher, year, area, id))
        conn.commit()
        conn.close()
        return redirect(url_for('list_investigations'))
    conn.close()
    return render_template('edit_investigation.html', record=record)

@app.route('/delete/investigation/<int:id>')
def delete_investigation(id):
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("DELETE FROM investigations WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('list_investigations'))

@app.route('/books')
def list_books():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("SELECT * FROM books")
    records = c.fetchall()
    conn.close()
    return render_template('list_books.html', records=records)

@app.route('/create/book', methods=['GET', 'POST'])
def create_book():
    if request.method == 'POST':
        title = request.form['title']
        author = request.form['author']
        year = request.form['year']
        publisher = request.form['publisher']
        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()
        c.execute("INSERT INTO books (title, author, year, publisher) VALUES (?, ?, ?, ?)", (title, author, year, publisher))
        conn.commit()
        conn.close()
        return redirect(url_for('list_books'))
    return render_template('create_book.html')

@app.route('/edit/book/<int:id>', methods=['GET', 'POST'])
def edit_book(id):
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("SELECT * FROM books WHERE id=?", (id,))
    record = c.fetchone()
    if request.method == 'POST':
        title = request.form['title']
        author = request.form['author']
        year = request.form['year']
        publisher = request.form['publisher']
        c.execute("UPDATE books SET title=?, author=?, year=?, publisher=? WHERE id=?", (title, author, year, publisher, id))
        conn.commit()
        conn.close()
        return redirect(url_for('list_books'))
    conn.close()
    return render_template('edit_book.html', record=record)

@app.route('/delete/book/<int:id>')
def delete_book(id):
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("DELETE FROM books WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('list_books'))

# Ruta para estadísticas
@app.route('/stats')
def show_stats():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("SELECT year, COUNT(*) FROM publications GROUP BY year")
    data = c.fetchall()
    conn.close()

    years = [row[0] for row in data]
    counts = [row[1] for row in data]

    bar = go.Bar(x=years, y=counts)
    layout = go.Layout(title='Publicaciones por Año')
    fig = go.Figure(data=[bar], layout=layout)
    plot_div = plot(fig, output_type='div')

    return render_template('stats.html', plot_div=plot_div)

if __name__ == '__main__':
    app.run(debug=True)
