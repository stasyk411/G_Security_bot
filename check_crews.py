import sqlite3
conn = sqlite3.connect('objects.db')
cursor = conn.cursor()
cursor.execute("SELECT id, name, telegram_id, status FROM gbr_crews")
rows = cursor.fetchall()
for row in rows:
    print(f"ID: {row[0]}, Name: {row[1]}, Telegram ID: {row[2]}, Status: {row[3]}")
conn.close()