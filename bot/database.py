import sqlite3
from datetime import datetime

def init_db():
    """Создаёт базу данных и таблицы."""
    conn = sqlite3.connect("bot_data.db")
    cursor = conn.cursor()
    
    # Участники
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS participants (
        user_id INTEGER PRIMARY KEY,
        username TEXT,
        added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # Шутки
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS jokes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        text TEXT NOT NULL,
        category TEXT DEFAULT 'general'
    )
    """)
    
    # Статистика (кто сколько пил)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS stats (
        user_id INTEGER,
        drinks INTEGER DEFAULT 0,
        FOREIGN KEY (user_id) REFERENCES participants (user_id)
    )
    """)
    
    conn.commit()
    conn.close()

def add_joke(text: str, category: str = "dark"):
    """Добавляет шутку в базу."""
    conn = sqlite3.connect("bot_data.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO jokes (text, category) VALUES (?, ?)", (text, category))
    conn.commit()
    conn.close()

def load_jokes_from_file(filename: str = "jokes.txt"):
    """Загружает шутки из файла в базу."""
    with open(filename, "r", encoding="utf-8") as file:
        jokes = [joke.strip() for joke in file.read().split("%%") if joke.strip()]
    
    conn = sqlite3.connect("bot_data.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM jokes")  # Очищаем старые шутки (опционально)
    
    for joke in jokes:
        cursor.execute("INSERT INTO jokes (text, category) VALUES (?, ?)", (joke, "dark"))
    
    conn.commit()
    conn.close()
    print(f"Загружено {len(jokes)} шуток.")

# Инициализация БД при первом запуске
init_db()
