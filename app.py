from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import sqlite3
import os

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins='*')

db_path = 'notepad.db'

def init_db():
    if not os.path.exists(db_path):
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE notes (id INTEGER PRIMARY KEY, content TEXT)''')
        cursor.execute("INSERT INTO notes (content) VALUES ('')")
        conn.commit()
        conn.close()

def get_text():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT content FROM notes WHERE id=1")
    text = cursor.fetchone()[0]
    conn.close()
    return text

def update_text(new_text):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("UPDATE notes SET content=? WHERE id=1", (new_text,))
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect')
def handle_connect():
    emit('update_text', get_text())

@socketio.on('text_update')
def handle_text_update(data):
    update_text(data)
    emit('update_text', data, broadcast=True)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True, allow_unsafe_werkzeug=True)

# Conteúdo do arquivo templates/index.html
index_html = """
<!DOCTYPE html>
<html lang='pt-br'>
<head>
    <meta charset='UTF-8'>
    <meta name='viewport' content='width=device-width, initial-scale=1.0'>
    <title>Notepad Compartilhado</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.0.1/socket.io.js"></script>
    <style>
        body {
            font-family: Arial, sans-serif;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            height: 100vh;
            background-color: #f4f4f4;
        }
        textarea {
            width: 80%;
            height: 400px;
            font-size: 16px;
            padding: 10px;
            border-radius: 5px;
            border: 1px solid #ccc;
        }
        button {
            margin-top: 10px;
            padding: 10px 20px;
            font-size: 16px;
            border: none;
            border-radius: 5px;
            background-color: #ff4d4d;
            color: white;
            cursor: pointer;
        }
    </style>
</head>
<body>
    <textarea id="notepad" placeholder="Digite aqui..."></textarea>
    <button onclick="clearText()">Apagar Tudo</button>
    <script>
        var socket = io();
        var textarea = document.getElementById('notepad');

        socket.on('update_text', function(data) {
            textarea.value = data;
        });

        textarea.addEventListener('input', function() {
            socket.emit('text_update', textarea.value);
        });

        function clearText() {
            textarea.value = "";
            socket.emit('text_update', "");
        }
    </script>
</body>
</html>
"""

# Salva o HTML no diretório correto
templates_dir = 'templates'
if not os.path.exists(templates_dir):
    os.makedirs(templates_dir)

with open(os.path.join(templates_dir, 'index.html'), 'w', encoding='utf-8') as f:
    f.write(index_html)
