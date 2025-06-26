from flask import Flask, request, render_template, redirect, url_for, send_from_directory, flash, session
import sqlite3
import os
from werkzeug.utils import secure_filename
from functools import wraps

app = Flask(__name__)
app.secret_key = 'your_secret_key'

UPLOAD_FOLDER = 'ebooks'
ALLOWED_EXTENSIONS = {'pdf'}
DB_FILE = 'books.db'

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('user_id'):
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            filename TEXT NOT NULL UNIQUE,
            category TEXT NOT NULL,
            sub_category TEXT
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS course_note (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            content TEXT
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            is_admin INTEGER NOT NULL DEFAULT 0
        )
    ''')
    conn.commit()
    conn.close()

def create_admin():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO users (username, password, is_admin) VALUES (?, ?, ?)",
              ("admin", "admin123", 1))
    conn.commit()
    conn.close()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_books(search_keyword=None):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    if search_keyword:
        c.execute("SELECT id, title, filename, category, sub_category FROM books WHERE title LIKE ?", ('%' + search_keyword + '%',))
    else:
        c.execute("SELECT id, title, filename, category, sub_category FROM books")
    books = c.fetchall()
    conn.close()

    books_by_category = {}
    course_books = {"课程1": [], "课程2": []}
    for book in books:
        id, title, filename, category, sub_category = book
        if category == "课程资料":
            if sub_category in course_books:
                course_books[sub_category].append({'id': id, 'title': title, 'filename': filename})
            else:
                course_books.setdefault("其他", []).append({'id': id, 'title': title, 'filename': filename})
        else:
            books_by_category.setdefault(category, []).append({'id': id, 'title': title, 'filename': filename})

    return books_by_category, course_books

def get_note():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT content FROM course_note WHERE id=1")
    row = c.fetchone()
    conn.close()
    return row[0] if row else ""

@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    search_keyword = ""
    if request.method == "POST":
        search_keyword = request.form.get("search", "")
    books_by_category, course_books = get_books(search_keyword)
    note = get_note()
    return render_template("index.html", books_by_category=books_by_category,
                           course_books=course_books, course_note=note,
                           search_keyword=search_keyword)

@app.route("/upload", methods=["POST"])
@login_required
def upload():
    if not session.get("is_admin"):
        flash("无权限上传")
        return redirect(url_for("index"))
    file = request.files["file"]
    title = file.filename.rsplit('.', 1)[0]
    category = request.form.get("category", "其他")
    sub_category = request.form.get("sub_category", "")

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        save_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(save_path)

        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        try:
            c.execute("INSERT INTO books (title, filename, category, sub_category) VALUES (?, ?, ?, ?)",
                      (title, filename, category, sub_category))
            conn.commit()
            flash("上传成功")
        except sqlite3.IntegrityError:
            flash("该 PDF 已存在")
        conn.close()
    return redirect(url_for("index"))

@app.route("/ebooks/<path:filename>")
@login_required
def serve_pdf(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

@app.route("/delete/<int:book_id>")
@login_required
def delete_book(book_id):
    if not session.get("is_admin"):
        flash("无权限删除")
        return redirect(url_for("index"))
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT filename FROM books WHERE id=?", (book_id,))
    row = c.fetchone()
    if row:
        try:
            os.remove(os.path.join(UPLOAD_FOLDER, row[0]))
        except FileNotFoundError:
            pass
        c.execute("DELETE FROM books WHERE id=?", (book_id,))
        conn.commit()
    conn.close()
    return redirect(url_for("index"))

@app.route("/rename_book/<int:book_id>", methods=["POST"])
@login_required
def rename_book(book_id):
    if not session.get("is_admin"):
        flash("无权限重命名")
        return redirect(url_for("index"))
    new_title = request.form.get("new_title", "")
    if new_title:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("UPDATE books SET title=? WHERE id=?", (new_title, book_id))
        conn.commit()
        conn.close()
    return redirect(url_for("index"))

@app.route("/update_course_note", methods=["POST"])
@login_required
def update_course_note():
    if not session.get("is_admin"):
        flash("无权限修改备注")
        return redirect(url_for("index"))
    content = request.form.get("course_note", "")
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO course_note (id, content) VALUES (1, ?)", (content,))
    conn.commit()
    conn.close()
    return redirect(url_for("index"))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("SELECT id, is_admin FROM users WHERE username=? AND password=?", (username, password))
        user = c.fetchone()
        conn.close()
        if user:
            session["user_id"] = user[0]
            session["is_admin"] = bool(user[1])
            session["username"] = username
            flash("登录成功")
            return redirect(url_for("index"))
        else:
            flash("用户名或密码错误")
    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if username.lower() == "admin":
            flash("不允许注册为 admin 用户名")
            return redirect(url_for("register"))

        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        try:
            c.execute("INSERT INTO users (username, password, is_admin) VALUES (?, ?, 0)", (username, password))
            conn.commit()
            flash("注册成功，请登录")
            return redirect(url_for("login"))
        except sqlite3.IntegrityError:
            flash("用户名已存在")
        finally:
            conn.close()
    return render_template("register.html")

@app.route("/logout")
@login_required
def logout():
    session.clear()
    flash("已退出登录")
    return redirect(url_for("login"))

if __name__ == "__main__":
    init_db()
    create_admin()
    app.run(debug=True, host="0.0.0.0", port=5000)
