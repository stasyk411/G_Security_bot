import os
import requests
from dotenv import load_dotenv

load_dotenv()
DADATA_API_KEY = os.getenv('DADATA_API_KEY')

print(f"Используем ключ: {DADATA_API_KEY[:5]}...{DADATA_API_KEY[-5:]}")

url = "https://suggestions.dadata.ru/suggestions/api/4_1/rs/suggest/address"
headers = {
    "Content-Type": "application/json",
    "Accept": "application/json",
    "Authorization": f"Token {DADATA_API_KEY}"
}
data = {"query": "Москва Кремль", "count": 1}

try:
    response = requests.post(url, headers=headers, json=data)
    print(f"Статус ответа: {response.status_code}")
    print(f"Тело ответа: {response.text[:200]}...")
except Exception as e:
    print(f"Ошибка: {e}")
    