import sqlite3

DB_NAME = "data.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Таблица пользователей
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        username TEXT,
        full_name TEXT,
        karma INTEGER DEFAULT 0
    )
    ''')

    # Таблица кружков
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS videos (
        user_id INTEGER PRIMARY KEY,
        file_id TEXT
    )
    ''')

    # Таблица оценок (лайки/дизлайки)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS ratings (
        from_user INTEGER,
        to_user INTEGER,
        rating_type TEXT,
        UNIQUE(from_user, to_user)
    )
    ''')

    conn.commit()
    conn.close()

init_db()

def add_user(user_id, username, full_name):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
    INSERT OR IGNORE INTO users (user_id, username, full_name)
    VALUES (?, ?, ?)
    ''', (user_id, username, full_name))
    conn.commit()
    conn.close()

def save_video(user_id, file_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
    INSERT OR REPLACE INTO videos (user_id, file_id)
    VALUES (?, ?)
    ''', (user_id, file_id))
    conn.commit()
    conn.close()

def get_video_by_user(user_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT file_id FROM videos WHERE user_id = ?', (user_id,))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else None

def update_karma(user_id, delta):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('UPDATE users SET karma = karma + ? WHERE user_id = ?', (delta, user_id))
    conn.commit()
    conn.close()

def has_voted(voter_id, user_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT 1 FROM ratings WHERE from_user = ? AND to_user = ?', (voter_id, user_id))
    result = cursor.fetchone()
    conn.close()
    return result is not None

def add_feedback(voter_id, user_id, rating_type):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
    INSERT OR IGNORE INTO ratings (from_user, to_user, rating_type)
    VALUES (?, ?, ?)
    ''', (voter_id, user_id, rating_type))
    conn.commit()
    conn.close()

def count_dislikes(user_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM ratings WHERE to_user = ? AND rating_type = "dislike"', (user_id,))
    count = cursor.fetchone()[0]
    conn.close()
    return count

def format_karma_table():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT username, full_name, karma FROM users ORDER BY karma DESC')
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        return "📊 Карма пока не выставлена никому."

    table = "🏆 Топ пользователей:\n"
    for i, (username, full_name, score) in enumerate(rows, 1):
        name = f"@{username}" if username else full_name
        table += f"{i}. {name}: {score}\n"
    return table

def get_user_score(user_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT karma FROM users WHERE user_id = ?', (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else 0