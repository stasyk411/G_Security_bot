import sqlite3

conn = sqlite3.connect('objects.db')
cursor = conn.cursor()

cursor.execute("SELECT name, address FROM objects")
rows = cursor.fetchall()

print("Объекты в базе:")
for row in rows:
    print(f"- {row[0]}: {row[1]}")

conn.close()