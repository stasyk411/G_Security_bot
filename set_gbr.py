import sqlite3

conn = sqlite3.connect('objects.db')
cursor = conn.cursor()

# Назначаем вас ГБР-1
cursor.execute("UPDATE gbr_crews SET telegram_id = '5986066094' WHERE name = 'ГБР-1'")

# Проверяем
cursor.execute("SELECT name, telegram_id, status FROM gbr_crews")
crews = cursor.fetchall()
print("Текущие экипажи:")
for crew in crews:
    print(f"  {crew[0]}: telegram_id={crew[1]}, статус={crew[2]}")

conn.commit()
conn.close()