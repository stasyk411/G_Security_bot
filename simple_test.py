import sqlite3

conn = sqlite3.connect('objects.db')
cursor = conn.cursor()

# Простейший запрос
cursor.execute("SELECT name FROM objects")
all_names = cursor.fetchall()

print("=== ВСЕ НАЗВАНИЯ В БАЗЕ ===")
for name in all_names:
    print(f'"{name[0]}"')

# Пробуем найти "магазин"
print("\n=== ПОИСК 'магазин' ===")
cursor.execute("SELECT name FROM objects WHERE name LIKE '%магазин%'")
found = cursor.fetchall()
print(f"Найдено: {len(found)}")
for item in found:
    print(f'  - {item[0]}')

conn.close()