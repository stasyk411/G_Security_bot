import sqlite3

conn = sqlite3.connect('objects.db')
cursor = conn.cursor()

# Проверяем все таблицы
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()

print("=== ТАБЛИЦЫ В БАЗЕ ===")
for table in tables:
    print(f" - {table[0]}")

# Проверяем структуру gbr_crews если есть
if ('gbr_crews',) in tables:
    cursor.execute("PRAGMA table_info(gbr_crews)")
    columns = cursor.fetchall()
    print("\n=== СТРУКТУРА gbr_crews ===")
    for col in columns:
        print(f" {col[1]} ({col[2]})")

conn.close()