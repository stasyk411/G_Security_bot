import os
import logging
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import requests
import json

# Загрузка переменных окружения
load_dotenv()

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Получение токенов из переменных окружения
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
DADATA_API_KEY = os.getenv('DADATA_API_KEY')


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /start"""
    welcome_message = (
        "👋 Привет! Я GBR Security Bot!\n\n"
        "Я помогу вам преобразовать адрес в ссылку на Яндекс.Карты.\n\n"
        "Просто отправьте мне адрес, например:\n"
        "• Ленина 5\n"
        "• Москва, Тверская улица, 1\n"
        "• Санкт-Петербург, Невский проспект, 50\n\n"
        "Я найду координаты и пришлю вам ссылку на карту!"
    )
    await update.message.reply_text(welcome_message)


async def handle_address(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик текстовых сообщений с адресом"""
    address = update.message.text
    
    # Отправляем сообщение о начале обработки
    await update.message.reply_text("🔍 Ищу адрес на карте...")
    
    try:
        # Получаем координаты через DaData API
        coordinates = get_coordinates_from_dadata(address)
        
        if coordinates:
            lat, lon = coordinates['lat'], coordinates['lon']
            
            # Формируем ссылку на Яндекс.Карты
            yandex_maps_url = f"https://yandex.ru/maps/?rtext=~{lat},{lon}"
            
            # Формируем ответное сообщение
            response_message = (
                f"📍 Адрес найден!\n\n"
                f"🏠 {coordinates['address']}\n"
                f"📊 Координаты: {lat:.6f}, {lon:.6f}\n\n"
                f"🗺️ Ссылка на Яндекс.Карты:\n{yandex_maps_url}"
            )
            
            await update.message.reply_text(response_message)
        else:
            await update.message.reply_text(
                "❌ Не удалось найти указанный адрес.\n"
                "Пожалуйста, проверьте правильность написания и попробуйте снова."
            )
            
    except Exception as e:
        logger.error(f"Error processing address: {e}")
        await update.message.reply_text(
            "⚠️ Произошла ошибка при обработке адреса.\n"
            "Пожалуйста, попробуйте позже."
        )


def get_coordinates_from_dadata(address):
    """Получение координат адреса через DaData API"""
    url = "https://suggestions.dadata.ru/suggestions/api/4_1/rs/suggest/address"
    
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Token {DADATA_API_KEY}"
    }
    
    data = {
        "query": address,
        "count": 1
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        
        result = response.json()
        
        if result['suggestions']:
            suggestion = result['suggestions'][0]
            data = suggestion['data']
            
            if 'geo_lat' in data and 'geo_lon' in data:
                return {
                    'lat': float(data['geo_lat']),
                    'lon': float(data['geo_lon']),
                    'address': suggestion['value']
                }
        
        return None
        
    except requests.exceptions.RequestException as e:
        logger.error(f"DaData API request error: {e}")
        return None
    except (KeyError, ValueError) as e:
        logger.error(f"DaData API response parsing error: {e}")
        return None


def main():
    """Основная функция запуска бота"""
    if not TELEGRAM_BOT_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN не найден в переменных окружения!")
        return
    
    if not DADATA_API_KEY:
        logger.error("DADATA_API_KEY не найден в переменных окружения!")
        return
    
    # Создаем приложение
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    # Добавляем обработчики
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_address))
    
    # Запускаем бота
    logger.info("Запуск GBR Security Bot...")
    application.run_polling()


if __name__ == '__main__':
    main()
