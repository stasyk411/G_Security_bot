import sqlite3
import os

db_path = 'objects.db'
print(f"Создаём таблицу в: {os.path.abspath(db_path)}")

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Создаём таблицу для ГБР
cursor.execute('''
CREATE TABLE IF NOT EXISTS gbr_crews (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    telegram_id TEXT UNIQUE,
    status TEXT DEFAULT 'free',
    last_active TIMESTAMP,
    notes TEXT
)
''')

# Добавляем тестовые экипажи
test_crews = [
    ('ГБР-1', None, 'free', 'Основной экипаж'),
    ('ГБР-2', None, 'free', 'Резервный экипаж')
]

for crew in test_crews:
    cursor.execute('''
        INSERT OR IGNORE INTO gbr_crews (name, telegram_id, status, notes)
        VALUES (?, ?, ?, ?)
    ''', crew)

conn.commit()

# Проверяем, что создалось
cursor.execute("SELECT name FROM gbr_crews")
crews = cursor.fetchall()
print(f"Созданы экипажи: {crews}")

conn.close()