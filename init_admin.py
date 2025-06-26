import sqlite3

def init_admin():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    # 创建 users 表（如果不存在）
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            is_admin INTEGER NOT NULL DEFAULT 0
        )
    ''')

    # 插入管理员账号（用户名：admin，密码：admin123）
    try:
        cursor.execute('''
            INSERT INTO users (username, password, is_admin)
            VALUES (?, ?, ?)
        ''', ('admin', 'admin123', 1))
        print("管理员账号初始化成功！用户名：admin，密码：admin123")
    except sqlite3.IntegrityError:
        print("管理员账号已存在，无需重复初始化。")
    finally:
        conn.commit()
        conn.close()

if __name__ == '__main__':
    init_admin()
