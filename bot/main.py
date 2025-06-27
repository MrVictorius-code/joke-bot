from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext
import sqlite3
import random
from database import load_jokes_from_file

# Настройки
TOKEN = "ВАШ_TELEGRAM_BOT_TOKEN"
ADMIN_ID = 123456789  # Ваш ID в Telegram

# Загружаем шутки из файла
load_jokes_from_file("bot/jokes.txt")

def start(update: Update, context: CallbackContext):
    update.message.reply_text(
        "Привет! Я бот для игры 'Стыдный смех'. "
        "Добавься в игру: /addme"
    )

def addme(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    username = update.effective_user.username
    
    conn = sqlite3.connect("bot_data.db")
    cursor = conn.cursor()
    
    # Добавляем участника, если его ещё нет
    cursor.execute(
        "INSERT OR IGNORE INTO participants (user_id, username) VALUES (?, ?)",
        (user_id, username)
    )
    
    # Добавляем запись в статистику
    cursor.execute(
        "INSERT OR IGNORE INTO stats (user_id, drinks) VALUES (?, 0)",
        (user_id,)
    )
    
    conn.commit()
    conn.close()
    update.message.reply_text("✅ Ты в игре! Теперь можешь получать шутки: /joke")

def joke(update: Update, context: CallbackContext):
    conn = sqlite3.connect("bot_data.db")
    cursor = conn.cursor()
    
    # Проверяем, есть ли участники
    cursor.execute("SELECT COUNT(*) FROM participants")
    if cursor.fetchone()[0] < 2:
        update.message.reply_text("Нужно минимум 2 участника! Добавь друзей: /addme")
        return
    
    # Выбираем случайную шутку
    cursor.execute("SELECT text FROM jokes ORDER BY RANDOM() LIMIT 1")
    joke_text = cursor.fetchone()[0]
    
    # Выбираем жертву (читает) и цель (слушает)
    cursor.execute("SELECT user_id, username FROM participants ORDER BY RANDOM() LIMIT 2")
    users = cursor.fetchall()
    victim_id, victim_name = users[0][0], users[0][1]
    target_id, target_name = users[1][0], users[1][1]
    
    # Отправляем шутку "жертве"
    context.bot.send_message(
        chat_id=victim_id,
        text=f"🎭 Прочитай вслух для @{target_name}:\n\n{joke_text}\n\n"
             "Если он засмеётся — пьёт он. Если ты — пьёшь ты! 🥃"
    )
    
    # Логируем
    print(f"Шутка отправлена: {victim_name} -> {target_name}")
    conn.close()

def main():
    updater = Updater(TOKEN)
    dispatcher = updater.dispatcher
    
    # Команды
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("addme", addme))
    dispatcher.add_handler(CommandHandler("joke", joke))
    
    # Запуск
    updater.start_polling()
    print("Бот запущен!")
    updater.idle()

if __name__ == "__main__":
    main()
