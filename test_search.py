import sqlite3

print("🔍 ПРОВЕРКА ПОИСКА В БАЗЕ ДАННЫХ")
print("=" * 40)

# Подключаемся к базе
conn = sqlite3.connect('objects.db')
cursor = conn.cursor()

# Смотрим все объекты в базе
print("\n📋 ВСЕ ОБЪЕКТЫ В БАЗЕ:")
cursor.execute("SELECT id, name, address FROM objects ORDER BY id")
all_objects = cursor.fetchall()
for obj in all_objects:
    print(f"  {obj[0]}. {obj[1]} — {obj[2]}")

# Тест 1: поиск по слову "магазин" (прямой LIKE)
print("\n🔎 ТЕСТ 1: Поиск 'магазин' (прямой LIKE)")
cursor.execute("SELECT name, address FROM objects WHERE name LIKE '%магазин%'")
results = cursor.fetchall()
print(f"Найдено: {len(results)}")
for r in results:
    print(f"  ✓ {r[0]} — {r[1]}")

# Тест 2: поиск с lower()
print("\n🔎 ТЕСТ 2: Поиск 'магазин' (с lower())")
cursor.execute("SELECT name, address FROM objects WHERE lower(name) LIKE lower('%магазин%')")
results = cursor.fetchall()
print(f"Найдено: {len(results)}")
for r in results:
    print(f"  ✓ {r[0]} — {r[1]}")

# Тест 3: поиск по слову "Продукты"
print("\n🔎 ТЕСТ 3: Поиск 'Продукты'")
cursor.execute("SELECT name, address FROM objects WHERE name LIKE '%Продукты%'")
results = cursor.fetchall()
print(f"Найдено: {len(results)}")
for r in results:
    print(f"  ✓ {r[0]} — {r[1]}")

# Тест 4: поиск по слову "Аптека"
print("\n🔎 ТЕСТ 4: Поиск 'Аптека'")
cursor.execute("SELECT name, address FROM objects WHERE name LIKE '%Аптека%'")
results = cursor.fetchall()
print(f"Найдено: {len(results)}")
for r in results:
    print(f"  ✓ {r[0]} — {r[1]}")

conn.close()
print("\n" + "=" * 40)
print("✅ ПРОВЕРКА ЗАВЕРШЕНА")