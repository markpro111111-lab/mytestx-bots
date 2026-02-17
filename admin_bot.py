#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import sqlite3
import time
import requests
import base64
import os
from datetime import datetime

ADMIN_BOT_TOKEN = "8545261117:AAEEw7pqWmEWnROf3e0IKVQNL_-qtLT7ges"
SUPER_ADMIN_ID = 7693302440
GITHUB_TOKEN = "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"
REPO_NAME = "markpro1111111-lab/mytestx-final"
GITHUB_API_URL = f"https://api.github.com/repos/{REPO_NAME}/contents"

bot = telebot.TeleBot(ADMIN_BOT_TOKEN)

conn = sqlite3.connect('admin_logs.db', check_same_thread=False)
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        action TEXT,
        details TEXT,
        timestamp DATETIME
    )
''')
conn.commit()

def log(action, details=""):
    cursor.execute('INSERT INTO logs (action, details, timestamp) VALUES (?, ?, ?)',
                   (action, details, datetime.now()))
    conn.commit()

def is_admin(user_id):
    return user_id == SUPER_ADMIN_ID

def update_file_on_github(file_path, new_content, commit_message):
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    r = requests.get(f"{GITHUB_API_URL}/{file_path}", headers=headers)
    sha = r.json().get("sha") if r.status_code == 200 else None
    encoded = base64.b64encode(new_content.encode()).decode()
    data = {
        "message": commit_message,
        "content": encoded,
        "sha": sha
    }
    r = requests.put(f"{GITHUB_API_URL}/{file_path}", headers=headers, json=data)
    return r.status_code in [200, 201]

@bot.message_handler(commands=['start'])
def start(message):
    if not is_admin(message.from_user.id):
        bot.reply_to(message, "⛔ Доступ запрещён")
        return
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton("📊 Статус", callback_data="status"),
        InlineKeyboardButton("📝 Логи", callback_data="logs"),
        InlineKeyboardButton("📢 Рассылка", callback_data="broadcast"),
        InlineKeyboardButton("🔄 Перезапуск", callback_data="restart"),
        InlineKeyboardButton("📥 Обновить код", callback_data="update_menu")
    )
    bot.reply_to(
        message,
        "🔧 **АДМИН-ПАНЕЛЬ**\n\nОтправь мне файл для обновления: main_bot.py, admin_bot.py, client_template.bat",
        parse_mode='Markdown',
        reply_markup=keyboard
    )

@bot.callback_query_handler(func=lambda call: call.data == "update_menu")
def update_menu_callback(call):
    if not is_admin(call.from_user.id):
        return
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        InlineKeyboardButton("📦 main_bot.py", callback_data="update_main"),
        InlineKeyboardButton("🔧 admin_bot.py", callback_data="update_admin"),
        InlineKeyboardButton("📄 client_template.bat", callback_data="update_template"),
        InlineKeyboardButton("◀️ Назад", callback_data="back_to_main")
    )
    bot.edit_message_text(
        "📥 **Какой файл обновить?**\n\nИли просто отправь мне файл.",
        call.message.chat.id,
        call.message.message_id,
        parse_mode='Markdown',
        reply_markup=keyboard
    )

@bot.message_handler(content_types=['document'])
def handle_document(message):
    if not is_admin(message.from_user.id):
        return
    file_name = message.document.file_name
    allowed = ["main_bot.py", "admin_bot.py", "client_template.bat"]
    if file_name not in allowed:
        bot.reply_to(message, "❌ Можно обновлять только: main_bot.py, admin_bot.py, client_template.bat")
        return
    bot.reply_to(message, f"⏳ Скачиваю {file_name}...")
    file_info = bot.get_file(message.document.file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    try:
        content = downloaded_file.decode('utf-8')
    except:
        bot.reply_to(message, "❌ Файл должен быть в UTF-8")
        return
    bot.reply_to(message, f"⏳ Отправляю в GitHub...")
    success = update_file_on_github(file_name, content, f"📥 Обновление {file_name} через Telegram")
    if success:
        bot.reply_to(message, f"✅ {file_name} обновлён!")
        log("ОБНОВЛЕНИЕ", f"{file_name}")
    else:
        bot.reply_to(message, f"❌ Ошибка при обновлении")

@bot.callback_query_handler(func=lambda call: call.data == "status")
def status_callback(call):
    if not is_admin(call.from_user.id):
        return
    main_conn = sqlite3.connect('shop.db')
    main_cursor = main_conn.cursor()
    main_cursor.execute('SELECT COUNT(*) FROM users')
    users = main_cursor.fetchone()[0]
    main_cursor.execute('SELECT COUNT(*) FROM users WHERE expiry > ?', (datetime.now(),))
    active = main_cursor.fetchone()[0]
    main_conn.close()
    text = f"""
📊 **СТАТИСТИКА**
━━━━━━━━━━━━━━━━━━━━━
👥 Всего пользователей: {users}
✅ Активных подписок: {active}
⏰ Время: {datetime.now().strftime('%H:%M:%S')}
━━━━━━━━━━━━━━━━━━━━━
"""
    bot.edit_message_text(text, call.message.chat.id, call.message.message_id, parse_mode='Markdown')

@bot.callback_query_handler(func=lambda call: call.data == "logs")
def logs_callback(call):
    if not is_admin(call.from_user.id):
        return
    cursor.execute('SELECT * FROM logs ORDER BY timestamp DESC LIMIT 10')
    logs = cursor.fetchall()
    text = "📝 **ПОСЛЕДНИЕ ДЕЙСТВИЯ**\n━━━━━━━━━━━━━━━━━━━━━\n"
    for log_entry in logs:
        text += f"\n🕐 {log_entry[3][:19]}\n⚡ {log_entry[1]}: {log_entry[2]}\n━━━━━━━━━━━━━━━━━━━━━\n"
    bot.edit_message_text(text, call.message.chat.id, call.message.message_id, parse_mode='Markdown')

@bot.callback_query_handler(func=lambda call: call.data == "broadcast")
def broadcast_callback(call):
    if not is_admin(call.from_user.id):
        return
    msg = bot.send_message(call.message.chat.id, "📢 **ВВЕДИ ТЕКСТ РАССЫЛКИ:**", parse_mode='Markdown')
    bot.register_next_step_handler(msg, process_broadcast)

def process_broadcast(message):
    if not is_admin(message.from_user.id):
        return
    text = message.text
    main_conn = sqlite3.connect('shop.db')
    main_cursor = main_conn.cursor()
    main_cursor.execute('SELECT user_id FROM users')
    users = main_cursor.fetchall()
    main_conn.close()
    sent = 0
    for user in users:
        try:
            bot.send_message(user[0], text, parse_mode='Markdown')
            sent += 1
            time.sleep(0.05)
        except:
            pass
    log("РАССЫЛКА", f"Отправлено {sent}")
    bot.reply_to(message, f"✅ Рассылка завершена! Отправлено: {sent}")

@bot.callback_query_handler(func=lambda call: call.data == "restart")
def restart_callback(call):
    if not is_admin(call.from_user.id):
        return
    bot.edit_message_text(
        "🔄 **Перезапуск через Render API**\n\nЭта функция будет добавлена позже.",
        call.message.chat.id,
        call.message.message_id,
        parse_mode='Markdown'
    )
    log("ПЕРЕЗАПУСК", "Запрошен перезапуск")

@bot.callback_query_handler(func=lambda call: call.data == "back_to_main")
def back_to_main_callback(call):
    if not is_admin(call.from_user.id):
        return
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton("📊 Статус", callback_data="status"),
        InlineKeyboardButton("📝 Логи", callback_data="logs"),
        InlineKeyboardButton("📢 Рассылка", callback_data="broadcast"),
        InlineKeyboardButton("🔄 Перезапуск", callback_data="restart"),
        InlineKeyboardButton("📥 Обновить код", callback_data="update_menu")
    )
    bot.edit_message_text(
        "🔧 **АДМИН-ПАНЕЛЬ**",
        call.message.chat.id,
        call.message.message_id,
        parse_mode='Markdown',
        reply_markup=keyboard
    )

if __name__ == "__main__":
    print("="*60)
    print("🔧 MY TEST X - АДМИН-БОТ")
    print("="*60)
    print("✅ Админ-бот запущен!")
    print("="*60)
    bot.infinity_polling()
