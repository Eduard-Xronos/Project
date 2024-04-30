from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask import Flask, render_template, request, jsonify
import sqlite3
import os
import re

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.secret_key = 'your_secret_key'
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    class_id = db.Column(db.Integer, db.ForeignKey('class.id'), nullable=False)

@app.route('/')
def index():
    with open('tecst.txt', 'r', encoding='utf-8') as file:
        rules = file.readlines()
    return render_template('index.html', rules=rules)

@app.route('/class/<class_name>')
def class_page(class_name):
    db_path = os.path.join("database.db")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT class, name FROM class WHERE class = ?", (class_name,))
    files = cursor.fetchall()
    conn.close()

    return render_template('class.html', class_name=class_name, books=files)


@app.route('/book/<book_id>')
def book_page(book_id):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT class FROM class WHERE name=?", (book_id,))
    audio_file = cursor.fetchone()[0]  # Получаем путь к аудиофайлу из базы данных
    conn.close()
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT comments FROM class WHERE name=?", (book_id,))
    file = cursor.fetchone()[0]  # Получаем путь к аудиофайлу из базы данных
    conn.close()
    return render_template('book.html', book_id=book_id, class_id=audio_file)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = generate_password_hash(password)

        # Проверяем, существует ли пользователь с таким именем
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            return render_template('register.html', error='Пользователь с таким именем уже существует')

        # Создаем нового пользователя
        new_user = User(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        # Возвращаемся на главную страницу
        return redirect(url_for('index'))

    # Если метод GET, просто отображаем страницу регистрации
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':  # Если форма отправлена
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()  # Проверяем наличие пользователя в базе данных

        if user and check_password_hash(user.password, password):  # Если пользователь найден и пароль верный
            session['username'] = username  # Записываем имя пользователя в сессию
            return redirect(url_for('index'))  # Перенаправляем на главную страницу
        else:
            return render_template('login.html', error='Неправильное имя пользователя или пароль')  # Отображаем сообщение об ошибке
    return render_template('login.html')  # Отображаем страницу входа

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))


from flask import render_template, send_file


@app.route('/audio/<book>')
def audio(book):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT audio FROM class WHERE name=?", (book,))
    audio_file = cursor.fetchone()[0]  # Получаем путь к аудиофайлу из базы данных
    conn.close()  # Закрываем соединение с базой данных
    audio_file = audio_file.split(',')
    books = audio_file[1]
    audio_file = audio_file[0]

    with open(audio_file, 'r', encoding='utf-8') as file:
        content = file.read()

    return render_template('audio.html', content=content, book=books, book_name=book)

@app.route('/movie/<book>')
def movie(book):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT movie FROM class WHERE name=?", (book,))
    audio_file = cursor.fetchone()[0]  # Получаем путь к аудиофайлу из базы данных
    conn.close()  # Закрываем соединение с базой данных
    audio_file = audio_file.split(',')
    books = audio_file[1]
    audio_file = audio_file[0]

    with open(audio_file, 'r', encoding='utf-8') as file:
        content = file.read()
    books = books.split('=')[1]
    content = content.split('\n')[0]

    return render_template('movie.html', content=content, book=books, book_name=book)

@app.route('/teatr/<book>')
def teatr(book):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT teatr FROM class WHERE name=?", (book,))
    audio_file = cursor.fetchone()[0]  # Получаем путь к аудиофайлу из базы данных
    conn.close()  # Закрываем соединение с базой данных
    audio_file = audio_file.split(',')[0]

    with open(audio_file, 'r', encoding='utf-8') as file:
        content = file.read()

    # Используем регулярное выражение для поиска ссылок и их замены на HTML-ссылки
    links = re.findall(r'(https?://\S+)', content)
    for i in range(len(links)):
        if '=' in links[i]:
            links[i] = "https://www.youtube.com/embed/" + links[i].split('=')[1]
    # Находим все ссылки в контенте

    content_with_links = re.sub(r'(https?://\S+)', r'<a href="\1">\1</a>', content)

    return render_template('teatr.html', content=content_with_links, book_name=book, silks=links)


@app.route('/interesting/<book>')
def interesting(book):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT interesting FROM class WHERE name=?", (book,))
    audio_file = cursor.fetchone()[0]  # Получаем путь к аудиофайлу из базы данных
    conn.close()  # Закрываем соединение с базой данных
    audio_file = audio_file.split(',')[0]

    with open(audio_file, 'r', encoding='utf-8') as file:
        content = file.read()

    return render_template('interesting.html', content=content, book_name=book)


@app.route('/vopros/<book>')
def vopros(book):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT vopros FROM class WHERE name=?", (book,))
    audio_file = cursor.fetchone()[0]  # Получаем путь к аудиофайлу из базы данных
    conn.close()  # Закрываем соединение с базой данных
    audio_file = audio_file.split(',')[0]

    with open(audio_file, 'r', encoding='utf-8') as file:
        content = file.read()

    return render_template('vopros.html', content=content, book_name=book, book_url=url_for('vopros', book=book))


@app.route('/image/<book>')
def image(book):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT image FROM class WHERE name=?", (book,))
    audio_file = cursor.fetchone()[0]  # Получаем путь к аудиофайлу из базы данных
    conn.close()  # Закрываем соединение с базой данных
    audio_file = audio_file.split(',')
    new = audio_file[0]
    file = audio_file[1]
    file = remov(file)
    file = str(file)

    with open(file, 'r', encoding='utf-8') as filed:
        content = filed.read()
    lines = content.strip().split("\n")

    # Инициализируем переменные
    name = ""
    name_av = ""
    imag = []

    name = lines[0]
    name_av = lines[1]
    imag = lines[2:]

    return render_template('image.html', name=name, avtor=name_av, n=imag, page=new, book=book)


def remov(input_str):
    # Удаляем точки
    input_str = input_str.replace("", "")

    # Удаляем скобки и кавычки
    input_str = input_str.replace("(", "")
    input_str = input_str.replace(")", "")
    input_str = input_str.replace("'", "")

    return input_str




@app.route('/kritic/<book>')
def kritic(book):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT kritic FROM class WHERE name=?", (book,))
    audio_file = cursor.fetchone()[0]  # Получаем путь к аудиофайлу из базы данных
    conn.close()  # Закрываем соединение с базой данных
    audio_file = audio_file.split(',')[0]

    with open(audio_file, 'r', encoding='utf-8') as file:
        content = file.read()

    # Используем регулярное выражение для поиска ссылок и их замены на HTML-ссылки
    links = re.findall(r'(https?://\S+)', content)
    for i in range(len(links)):
        if '=' in links[i]:
            links[i] = "https://www.youtube.com/embed/" + links[i].split('=')[1]
    # Находим все ссылки в контенте

    content_with_links = re.sub(r'(https?://\S+)', r'<a href="\1">\1</a>', content)

    return render_template('kritic.html', content=content_with_links, book_name=book, silks=links)


@app.route('/music/<book>')
def music(book):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT music FROM class WHERE name=?", (book,))
    audio_file = cursor.fetchone()[0]  # Получаем путь к аудиофайлу из базы данных
    conn.close()  # Закрываем соединение с базой данных
    audio_file = audio_file.split(',')[0]

    with open(audio_file, 'r', encoding='utf-8') as file:
        content = file.read()

    # Используем регулярное выражение для поиска ссылок и их замены на HTML-ссылки
    links = re.findall(r'(https?://\S+)', content)
    for i in range(len(links)):
        links[i] = links[i].split('=')[1]

    content_with_links = re.sub(r'(https?://\S+)', r'<a href="\1">\1</a>', content)

    return render_template('music.html', content=content_with_links, book_name=book, silks=links)

@app.route('/save_comment', methods=['POST'])
def save_comment_route():
    data = request.json
    username = data['username']
    comment = data['comment']
    save_comment(username, comment)
    return jsonify({'status': 'success', 'comment': username + ': ' + comment})

def save_comment(username, comment):
    with open('comments.txt', 'a') as file:
        file.write(username + ' <->=+ ' + comment.replace('\n', '<NEW_LINE>') + '\n')

@app.route('/load_comments')
def load_comments_route():
    comments = load_comments()
    return jsonify({'comments': comments})

def load_comments():
    comments = []
    with open('comments.txt', 'r') as file:
        current_comment = ''
        for line in file:
            if '<->=+' in line:
                if current_comment:
                    comments.append(current_comment.strip())
                parts = line.split('<->=+')
                username = parts[0].strip()
                comment = parts[1].strip()
                current_comment = username + ': ' + comment.replace('<NEW_LINE>', '\n')
            else:
                current_comment += ' ' + line.strip().replace('\\n', '\n')
        if current_comment:
            comments.append(current_comment.strip())
    return comments

if __name__ == '__main__':
    app.run(debug=True)

