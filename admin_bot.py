#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import sqlite3
import time
from datetime import datetime

ADMIN_BOT_TOKEN = "8545261117:AAFdfaOjNsGEdJzzesVGF3x_8II95vbsmzs"
SUPER_ADMIN_ID = 7693302440

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
        InlineKeyboardButton("🔄 Перезапуск", callback_data="restart")
    )
    bot.reply_to(message, "🔧 **АДМИН-ПАНЕЛЬ**\n\nВыбери действие:", parse_mode='Markdown', reply_markup=keyboard)

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
    for log in logs:
        text += f"\n🕐 {log[3][:19]}\n⚡ {log[1]}: {log[2]}\n━━━━━━━━━━━━━━━━━━━━━\n"
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
    log("РАССЫЛКА", f"Отправлено {sent} пользователям")
    bot.reply_to(message, f"✅ Рассылка завершена! Отправлено: {sent}")

@bot.callback_query_handler(func=lambda call: call.data == "restart")
def restart_callback(call):
    if not is_admin(call.from_user.id):
        return
    bot.edit_message_text("🔄 Перезапуск...", call.message.chat.id, call.message.message_id)
    log("ПЕРЕЗАПУСК", "Запрошен перезапуск бота")

if __name__ == "__main__":
    print("="*60)
    print("🔧 MY TEST X - АДМИН-БОТ")
    print("="*60)
    print("✅ Админ-бот запущен!")
    print("="*60)
    bot.infinity_polling()
