from flask import Flask, render_template, request, redirect, send_from_directory, abort
import sqlite3
import os

app = Flask(__name__)

def get_books():
    conn = sqlite3.connect('books.db')
    c = conn.cursor()
    c.execute("SELECT id, title, path FROM books;")
    books = c.fetchall()
    conn.close()
    return books

@app.route('/')
def index():
    books = get_books()
    return render_template('index.html', books=books)

@app.route('/delete/<int:book_id>')
def delete(book_id):
    conn = sqlite3.connect('books.db')
    c = conn.cursor()
    c.execute("DELETE FROM books WHERE id=?", (book_id,))
    conn.commit()
    conn.close()
    return redirect('/')

@app.route('/update/<int:book_id>', methods=['POST'])
def update(book_id):
    new_title = request.form['new_title']
    conn = sqlite3.connect('books.db')
    c = conn.cursor()
    c.execute("UPDATE books SET title=? WHERE id=?", (new_title, book_id))
    conn.commit()
    conn.close()
    return redirect('/')

@app.route('/search')
def search():
    keyword = request.args.get('q', '')
    conn = sqlite3.connect('books.db')
    c = conn.cursor()
    c.execute("SELECT id, title, path FROM books WHERE title LIKE ?", ('%'+keyword+'%',))
    results = c.fetchall()
    conn.close()
    return render_template('index.html', books=results)

@app.route('/pdfs/<path:filename>')
def serve_pdf(filename):
    if not filename.lower().endswith('.pdf'):
        abort(403)
    ebooks_dir = os.path.join(os.getcwd(), 'ebooks')
    return send_from_directory(ebooks_dir, filename)

if __name__ == '__main__':
    # 监听所有网卡，开启公网访问，端口5000
    app.run(host='0.0.0.0', port=5000, debug=True)
