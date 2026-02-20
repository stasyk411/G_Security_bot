import os
import logging
import sqlite3
from datetime import datetime
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
import requests

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

# Путь к базе данных
DB_PATH = 'objects.db'

# ID диспетчера (ваш)
DISPATCHER_ID = 5986066094

# Хранилище состояний поиска
user_search_state = {}


def get_crew_status(crew_id=None):
    """Получить статус экипажа(ей)"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    if crew_id:
        cursor.execute('SELECT id, name, status, telegram_id FROM gbr_crews WHERE id = ?', (crew_id,))
        result = cursor.fetchone()
        conn.close()
        return result
    else:
        cursor.execute('SELECT id, name, status, telegram_id FROM gbr_crews ORDER BY id')
        results = cursor.fetchall()
        conn.close()
        return results


def update_crew_status(crew_id, status, telegram_id=None):
    """Обновить статус экипажа"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    if telegram_id:
        cursor.execute('''
            UPDATE gbr_crews 
            SET status = ?, last_active = ?, telegram_id = ?
            WHERE id = ?
        ''', (status, datetime.now(), telegram_id, crew_id))
    else:
        cursor.execute('''
            UPDATE gbr_crews 
            SET status = ?, last_active = ?
            WHERE id = ?
        ''', (status, datetime.now(), crew_id))
    
    conn.commit()
    conn.close()


def search_objects(query):
    """Поиск объектов в базе данных"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Получаем ВСЕ объекты
    cursor.execute('SELECT id, name, address, category, notes, lat, lon FROM objects')
    all_objects = cursor.fetchall()
    conn.close()
    
    # Ищем в Python
    query_lower = query.lower()
    results = []
    
    for obj in all_objects:
        obj_id, name, address, category, notes, lat, lon = obj
        if query_lower in name.lower() or query_lower in address.lower():
            results.append(obj)
    
    logger.info(f"Поиск '{query}': найдено {len(results)} объектов")
    return results[:10]


def get_object_by_id(obj_id):
    """Получить объект по ID"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT id, name, address, category, notes, lat, lon FROM objects WHERE id = ?', (obj_id,))
    result = cursor.fetchone()
    conn.close()
    return result


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /start"""
    user_id = update.effective_user.id
    
    if user_id == DISPATCHER_ID:
        welcome_message = (
            "👋 Привет, диспетчер!\n\n"
            "Команды:\n"
            "/find [название] - найти объект в базе\n"
            "/status - показать статусы ГБР\n"
            "Или просто отправьте адрес для поиска в DaData"
        )
    else:
        # Это ГБР, проверяем, есть ли в базе
        crews = get_crew_status()
        crew_found = False
        
        for crew in crews:
            if crew[3] == str(user_id):
                crew_found = True
                update_crew_status(crew[0], 'free', str(user_id))
                break
        
        if crew_found:
            welcome_message = (
                "👋 Привет, ГБР!\n\n"
                "Твой статус: 🟢 Свободен\n\n"
                "Команды:\n"
                "/status - показать мой статус\n"
                "/busy - я занят (выехал)\n"
                "/arrived - я прибыл на место\n"
                "/free - я свободен\n"
                "/myid - показать мой ID"
            )
        else:
            welcome_message = (
                "❌ Ты не зарегистрирован как ГБР.\n"
                "Обратись к диспетчеру."
            )
    
    await update.message.reply_text(welcome_message)


async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Показать статусы"""
    user_id = update.effective_user.id
    
    if user_id == DISPATCHER_ID:
        # Диспетчер видит все статусы
        crews = get_crew_status()
        status_text = "📊 **СТАТУСЫ ГБР:**\n\n"
        
        status_emoji = {
            'free': '🟢 Свободен',
            'busy': '🔴 Занят',
            'arrived': '🏁 На месте'
        }
        
        for crew in crews:
            crew_id, name, status, telegram_id = crew
            status_text += f"{name}: {status_emoji.get(status, '⚪ Неизвестно')}\n"
        
        await update.message.reply_text(status_text)
    
    else:
        # ГБР видит свой статус
        crews = get_crew_status()
        for crew in crews:
            if crew[3] == str(user_id):
                status_emoji = {
                    'free': '🟢 Свободен',
                    'busy': '🔴 Занят',
                    'arrived': '🏁 На месте'
                }
                await update.message.reply_text(
                    f"Твой статус: {status_emoji.get(crew[2], '⚪ Неизвестно')}"
                )
                return
        
        await update.message.reply_text("❌ Ты не зарегистрирован как ГБР.")


async def busy_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """ГБР занят"""
    user_id = update.effective_user.id
    crews = get_crew_status()
    
    for crew in crews:
        if crew[3] == str(user_id):
            update_crew_status(crew[0], 'busy')
            await update.message.reply_text("✅ Статус изменён: 🔴 Занят")
            return
    
    await update.message.reply_text("❌ Ты не зарегистрирован как ГБР.")


async def arrived_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """ГБР прибыл"""
    user_id = update.effective_user.id
    crews = get_crew_status()
    
    for crew in crews:
        if crew[3] == str(user_id):
            update_crew_status(crew[0], 'arrived')
            await update.message.reply_text("✅ Статус изменён: 🏁 Прибыл на место")
            return
    
    await update.message.reply_text("❌ Ты не зарегистрирован как ГБР.")


async def free_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """ГБР свободен"""
    user_id = update.effective_user.id
    crews = get_crew_status()
    
    for crew in crews:
        if crew[3] == str(user_id):
            update_crew_status(crew[0], 'free')
            await update.message.reply_text("✅ Статус изменён: 🟢 Свободен")
            return
    
    await update.message.reply_text("❌ Ты не зарегистрирован как ГБР.")


async def myid_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Показать свой ID"""
    user_id = update.effective_user.id
    await update.message.reply_text(f"Твой Telegram ID: `{user_id}`", parse_mode='Markdown')


async def find_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /find (только для диспетчера)"""
    user_id = update.effective_user.id
    
    if user_id != DISPATCHER_ID:
        await update.message.reply_text("❌ Эта команда только для диспетчера.")
        return
    
    logger.info(f"Получена команда /find с аргументами: {context.args}")
    
    # Получаем текст после команды
    query = ' '.join(context.args) if context.args else ''
    
    if not query:
        await update.message.reply_text("Укажите название для поиска, например: /find магазин")
        return
    
    # Ищем в базе
    results = search_objects(query)
    
    if not results:
        await update.message.reply_text(f"По запросу '{query}' ничего не найдено.")
        return
    
    # Сохраняем результаты
    user_search_state[user_id] = results
    
    # Формируем клавиатуру
    keyboard = []
    for i, obj in enumerate(results[:5]):
        obj_id, name, address, category, notes, lat, lon = obj
        button_text = f"{i+1}. {name} ({address})"
        keyboard.append([InlineKeyboardButton(button_text, callback_data=f"select_{obj_id}")])
    
    if len(results) > 5:
        keyboard.append([InlineKeyboardButton("Показать все", callback_data="show_all")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        f"Найдено объектов: {len(results)}. Выберите:",
        reply_markup=reply_markup
    )


async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик нажатий на кнопки"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    
    if user_id != DISPATCHER_ID:
        await query.edit_message_text("❌ Только диспетчер может выбирать объекты.")
        return
    
    data = query.data
    
    if data.startswith("select_"):
        obj_id = int(data.split("_")[1])
        obj = get_object_by_id(obj_id)
        
        if obj:
            obj_id, name, address, category, notes, lat, lon = obj
            context.user_data['selected_object'] = obj
            
            # Получаем список ГБР со статусами
            crews = get_crew_status()
            
            # Формируем кнопки для выбора ГБР
            keyboard = []
            for crew in crews:
                crew_id, crew_name, status, telegram_id = crew
                
                # Статус эмодзи
                status_emoji = '🟢' if status == 'free' else '🔴' if status == 'busy' else '🏁'
                
                button_text = f"{status_emoji} {crew_name}"
                callback_data = f"send_{crew_id}_{obj_id}"
                keyboard.append([InlineKeyboardButton(button_text, callback_data=callback_data)])
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                f"Выбран объект:\n\n"
                f"🏠 {name}\n"
                f"📍 {address}\n"
                f"📝 {notes}\n\n"
                f"Кому отправить? (🟢 свободен, 🔴 занят, 🏁 на месте)",
                reply_markup=reply_markup
            )
    
    elif data.startswith("send_"):
        parts = data.split('_')
        crew_id = int(parts[1])
        obj_id = int(parts[2])
        
        obj = get_object_by_id(obj_id)
        crew_info = get_crew_status(crew_id)
        
        if obj and crew_info:
            obj_id, name, address, category, notes, lat, lon = obj
            crew_id, crew_name, crew_status, crew_telegram_id = crew_info
            
            # Формируем сообщение для ГБР
            navi_url = f"yandexnavi://build_route_on_map?lat_to={lat}&lon_to={lon}"
            maps_url = f"https://yandex.ru/maps/?rtext=~{lat},{lon}&rtab=auto"
            
            message = (
                f"🚨 Срабатывание: ТРЕВОГА\n"
                f"🏠 {name}\n"
                f"📍 {address}\n"
                f"📝 {notes}\n\n"
                f"🚗 <a href='{navi_url}'>Открыть в Навигаторе</a>\n"
                f"🗺️ <a href='{maps_url}'>Открыть в Картах</a>"
            )
            
            # Отправляем ГБР
            try:
                await context.bot.send_message(
                    chat_id=crew_telegram_id,
                    text=message,
                    parse_mode='HTML',
                    disable_web_page_preview=True
                )
                
                # Обновляем статус ГБР на busy
                update_crew_status(crew_id, 'busy')
                
                await query.edit_message_text(
                    f"✅ Вызов отправлен {crew_name}!\n\n{message}",
                    parse_mode='HTML'
                )
            except Exception as e:
                logger.error(f"Ошибка отправки ГБР: {e}")
                await query.edit_message_text(
                    f"❌ Не удалось отправить вызов. ГБР не зарегистрирован в боте?"
                )


async def handle_address(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик текстовых сообщений с адресом"""
    address = update.message.text
    
    # Отправляем сообщение о начале обработки
    await update.message.reply_text("🔍 Ищу адрес в DaData...")
    
    try:
        # Получаем координаты через DaData API
        coordinates = get_coordinates_from_dadata(address)
        
        if coordinates and coordinates.get('lat'):
            lat, lon = coordinates['lat'], coordinates['lon']
            
            # ССЫЛКА ДЛЯ НАВИГАТОРА
            navi_url = f"yandexnavi://build_route_on_map?lat_to={lat}&lon_to={lon}"
            
            # ССЫЛКА ДЛЯ КАРТ
            maps_url = f"https://yandex.ru/maps/?rtext=~{lat},{lon}&rtab=auto"
            
            # Формируем ответ
            response_message = (
                f"📍 Адрес найден в DaData!\n\n"
                f"🏠 {coordinates['address']}\n\n"
                f"🚗 <a href='{navi_url}'>Открыть в Навигаторе</a>\n"
                f"🗺️ <a href='{maps_url}'>Открыть в Картах</a>\n\n"
                f"📊 Координаты: {lat:.6f}, {lon:.6f}"
            )
            
            await update.message.reply_text(
                response_message,
                parse_mode='HTML',
                disable_web_page_preview=True
            )
        else:
            await update.message.reply_text(
                f"❌ Адрес не найден в DaData.\n"
                f"Попробуйте уточнить название."
            )
            
    except Exception as e:
        logger.error(f"Ошибка: {e}")
        await update.message.reply_text(
            f"⚠️ Ошибка при обработке.\n"
            f"Попробуйте позже."
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
        response = requests.post(url, headers=headers, json=data, timeout=10)
        
        if response.status_code != 200:
            logger.error(f"DaData ошибка {response.status_code}: {response.text}")
            return None
        
        result = response.json()
        
        if not result.get('suggestions'):
            return None
        
        suggestion = result['suggestions'][0]
        data = suggestion.get('data', {})
        
        if data.get('geo_lat') and data.get('geo_lon'):
            return {
                'lat': float(data['geo_lat']),
                'lon': float(data['geo_lon']),
                'address': suggestion['value']
            }
        else:
            return None
        
    except Exception as e:
        logger.error(f"Ошибка запроса к DaData: {e}")
        return None


def main():
    """Основная функция запуска бота"""
    if not TELEGRAM_BOT_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN не найден!")
        return
    
    if not DADATA_API_KEY:
        logger.error("DADATA_API_KEY не найден!")
        return
    
    # Создаем приложение
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    # Добавляем обработчики
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("status", status_command))
    application.add_handler(CommandHandler("busy", busy_command))
    application.add_handler(CommandHandler("arrived", arrived_command))
    application.add_handler(CommandHandler("free", free_command))
    application.add_handler(CommandHandler("myid", myid_command))
    application.add_handler(CommandHandler("find", find_command))
    application.add_handler(CallbackQueryHandler(button_callback))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_address))
    
    # Запускаем бота
    logger.info("Запуск GBR Security Bot (полный MVP)...")
    application.run_polling()


if __name__ == '__main__':
    main()