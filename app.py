import pandas as pd
import os
from flask import Flask, redirect, render_template, request
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

# Определение пути к базе данных
project_dir = os.path.dirname(os.path.abspath(__file__))
database_file = "sqlite:///{}".format(os.path.join(project_dir, "librarydatabase.db"))

# Инициализация Flask приложения
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = database_file
db = SQLAlchemy(app)
migrate = Migrate(app, db)


# Модель данных для таблицы авторов
class Author(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    books = db.relationship('Book', backref='author', lazy=True, cascade='all, delete-orphan')


# Модель данных для таблицы книг
class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(100), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('author.id', ondelete='CASCADE'), nullable=False)


# Функция для добавления авторов из CSV-файла в базу данных
def add_authors_from_csv(file_path):
    data = pd.read_csv(file_path)
    for name in data['name']:
        print(name)
        author = Author(name=name)
        db.session.add(author)
    db.session.commit()


# Функция для добавления книг из CSV-файла в базу данных
def add_books_from_csv(file_path):
    data = pd.read_csv(file_path)
    for index, row in data.iterrows():
        print(row)
        author_id = int(row['author_id'])
        author = Author.query.get(author_id)
        if author:
            book = Book(title=row['title'], author_id=author_id)
            db.session.add(book)
    db.session.commit()


# CRUD операции для таблицы Author
# Создание автора
@app.route('/author/create', methods=["POST"])
def create_author():
    if request.method == "POST":
        author_name = request.form.get("author_name")
        existing_author = Author.query.filter_by(name=author_name).first()

        if existing_author:
            return f"Author '{author_name}' already exists"
        elif author_name:
            new_author = Author(name=author_name)
            db.session.add(new_author)
            db.session.commit()
            return redirect('/')


# Получение информации об авторе
@app.route('/author/<int:author_id>', methods=["GET"])
def get_author(author_id):
    author = Author.query.get_or_404(author_id)
    return render_template('author.html', author=author)


# Обновление информации об авторе
@app.route('/author/<int:author_id>/update', methods=["POST"])
def update_author(author_id):
    if request.method == "POST":
        author = Author.query.get_or_404(author_id)
        new_name = request.form.get("new_name")
        author.name = new_name
        db.session.commit()
        return redirect('/')


# Удаление автора
@app.route('/author/<int:author_id>/delete', methods=["POST"])
def delete_author(author_id):
    author = Author.query.get_or_404(author_id)
    db.session.delete(author)
    db.session.commit()
    return redirect('/')


# CRUD операции для таблицы Book
# Создание книги
@app.route('/book/create', methods=["POST"])
def create_book():
    if request.method == "POST":
        title = request.form.get("title")
        author_id = request.form.get("author_id")
        new_book = Book(title=title, author_id=author_id)
        db.session.add(new_book)
        db.session.commit()
        return redirect('/')


# Получение информации о книге
@app.route('/book/<int:book_id>', methods=["GET"])
def get_book(book_id):
    book = Book.query.get_or_404(book_id)
    return render_template('book.html', book=book)


# Обновление информации о книге
@app.route('/book/<int:book_id>/update', methods=["POST"])
def update_book(book_id):
    if request.method == "POST":
        book = Book.query.get_or_404(book_id)
        new_title = request.form.get("new_title")
        book.title = new_title
        db.session.commit()
        return redirect('/')


# Удаление книги
@app.route('/book/<int:book_id>/delete', methods=["POST"])
def delete_book(book_id):
    book = Book.query.get_or_404(book_id)
    db.session.delete(book)
    db.session.commit()
    return redirect('/')


# Показать список книг
@app.route('/books')
def book_list():
    return render_template('books.html', books=Book.query.all())


# Показать список авторов
@app.route('/authors')
def author_list():
    return render_template('authors.html', authors=Author.query.all())


# Главная страница с общим списком авторов и книг
@app.route('/', methods=["GET", "POST"])
def home():
    authors = Author.query.all()
    books = Book.query.all()
    return render_template("home.html", authors=authors, books=books)


# Создание таблиц в базе данных, добавление данных из CSV-файлов и запуск приложения
if __name__ == '__main__':
    db.create_all()
    add_authors_from_csv('authors.csv')
    add_books_from_csv('books.csv')
    app.run()
