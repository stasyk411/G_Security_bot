import os
import logging
import sqlite3
from datetime import datetime
from dotenv import load_dotenv
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Загрузка переменных окружения
load_dotenv()

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Токен бота для ГБР (вставь сюда)
GBR_BOT_TOKEN = "ЗДЕСЬ_ТОКЕН_ТВОЕГО_GBR_Crew_bot"

# Путь к базе данных (общая с диспетчерским ботом)
DB_PATH = 'objects.db'

# Клавиатура с кнопками на русском
reply_keyboard = [
    [KeyboardButton("🔴 Занят")],
    [KeyboardButton("🏁 Прибыл")],
    [KeyboardButton("🟢 Свободен")]
]
main_keyboard = ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True)


def get_crew_by_telegram_id(telegram_id):
    """Найти ГБР по Telegram ID"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id, name, status FROM gbr_crews WHERE telegram_id = ?
    ''', (str(telegram_id),))
    result = cursor.fetchone()
    conn.close()
    return result


def update_crew_status(crew_id, status):
    """Обновить статус ГБР"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE gbr_crews 
        SET status = ?, last_active = ?
        WHERE id = ?
    ''', (status, datetime.now(), crew_id))
    conn.commit()
    conn.close()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Приветствие и регистрация ГБР"""
    user_id = update.effective_user.id
    username = update.effective_user.first_name
    
    # Проверяем, есть ли уже такой ГБР в базе
    crew = get_crew_by_telegram_id(user_id)
    
    if crew:
        crew_id, crew_name, status = crew
        await update.message.reply_text(
            f"👋 С возвращением, {crew_name}!\n"
            f"Твой текущий статус: {status}",
            reply_markup=main_keyboard
        )
    else:
        # Если ГБР нет в базе, предлагаем связаться с диспетчером
        await update.message.reply_text(
            "❌ Ты не зарегистрирован в системе как ГБР.\n"
            "Обратись к диспетчеру, чтобы добавить тебя в базу.",
            reply_markup=main_keyboard
        )


async def handle_status_change(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработка нажатий на кнопки"""
    user_id = update.effective_user.id
    text = update.message.text
    
    crew = get_crew_by_telegram_id(user_id)
    
    if not crew:
        await update.message.reply_text(
            "❌ Ты не зарегистрирован в системе.\n"
            "Напиши диспетчеру, чтобы добавили твой ID."
        )
        return
    
    crew_id, crew_name, current_status = crew
    
    status_map = {
        "🔴 Занят": "busy",
        "🏁 Прибыл": "arrived", 
        "🟢 Свободен": "free"
    }
    
    if text in status_map:
        new_status = status_map[text]
        update_crew_status(crew_id, new_status)
        
        status_messages = {
            "busy": "🔴 Статус изменён: Занят (выехал на вызов)",
            "arrived": "🏁 Статус изменён: Прибыл на место",
            "free": "🟢 Статус изменён: Свободен"
        }
        
        await update.message.reply_text(
            status_messages[new_status],
            reply_markup=main_keyboard
        )
        
        logger.info(f"ГБР {crew_name} сменил статус на {new_status}")
    else:
        await update.message.reply_text(
            "Используй кнопки для изменения статуса:",
            reply_markup=main_keyboard
        )


async def send_alert_to_gbr(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Эта функция будет вызываться из бота диспетчера"""
    # Пока заглушка, потом сделаем отправку
    pass


def main():
    """Запуск бота для ГБР"""
    if not GBR_BOT_TOKEN or GBR_BOT_TOKEN == "ЗДЕСЬ_ТОКЕН_ТВОЕГО_GBR_Crew_bot":
        logger.error("❌ Не вставлен токен бота для ГБР!")
        print("\n⚠️  ВНИМАНИЕ: Вставь токен в переменную GBR_BOT_TOKEN в начале файла!\n")
        return
    
    # Создаём приложение
    application = Application.builder().token(GBR_BOT_TOKEN).build()
    
    # Добавляем обработчики
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_status_change))
    
    # Запускаем бота
    logger.info("Запуск GBR Crew Bot...")
    print("✅ Бот для ГБР запущен. Готов к работе.")
    application.run_polling()


if __name__ == '__main__':
    main()