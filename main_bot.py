#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import sqlite3
import random
import string
import os
from datetime import datetime, timedelta

TOKEN = "8105894338:AAF5KSBv3vba5fA0-ohpBWWs-CfKBA7DDK0"
ADMIN_ID = 7693302440
SUPPORT_USERNAME = "@MyTestX_support"

bot = telebot.TeleBot(TOKEN)

conn = sqlite3.connect('shop.db', check_same_thread=False)
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        username TEXT,
        first_name TEXT,
        registered DATETIME,
        code TEXT,
        plan TEXT,
        expiry DATETIME
    )
''')
conn.commit()

PRICES = {
    'day': 25,
    'week': 100,
    'month': 300,
    'year': 1500
}

def generate_code(user_id):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

def create_client_file(user_id, code, plan):
    with open('client_template.bat', 'r', encoding='utf-8') as f:
        template = f.read()
    content = template.replace('{{USER_CODE}}', code).replace('{{USER_ID}}', str(user_id))
    filename = f"MyTestX_Client_{user_id}.bat"
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content)
    return filename

def send_manual(chat_id, code):
    manual = f"""
📚 ПОЛНЫЙ МАНУАЛ MY TEST X ULTIMATE

🔥 ЧТО ТЕБЕ НУЖНО ПОДГОТОВИТЬ ДОМА:

✅ Флешка (любая, от 1 ГБ)
✅ 5 минут свободного времени
✅ Файл, который я тебе отправил

💻 ПОДГОТОВКА ФЛЕШКИ:

1️⃣ Вставь флешку в компьютер
2️⃣ Скопируй на неё полученный файл

🏫 В КЛАССЕ ИНФОРМАТИКИ:

🔹 ШАГ 1: Сядь за любой компьютер
🔹 ШАГ 2: Вставь флешку
🔹 ШАГ 3: Запусти файл

⌨️ ГОРЯЧИЕ КЛАВИШИ:

🔹 Ctrl+Shift+F12 — АКТИВАЦИЯ
🔹 F8  — Поиск ответа
🔹 F9  — Авторежим
🔹 F10 — Скриншот
🔹 F11 — Статистика
🔹 Fn+Delete — Удаление

🎯 ТВОЙ КОД АКТИВАЦИИ: {code}
"""
    bot.send_message(chat_id, manual)

@bot.message_handler(commands=['start'])
def start(message):
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton("💎 Купить", callback_data="buy"),
        InlineKeyboardButton("📚 Мануал", callback_data="manual"),
        InlineKeyboardButton("👤 Мой аккаунт", callback_data="my_account"),
        InlineKeyboardButton("🆘 Поддержка", callback_data="support")
    )
    bot.reply_to(
        message,
        f"🔥 **MY TEST X ULTIMATE** 🔥\n\n"
        f"👤 Привет, {message.from_user.first_name}!\n\n"
        f"💎 Цены:\n"
        f"• День — {PRICES['day']}⭐\n"
        f"• Неделя — {PRICES['week']}⭐\n"
        f"• Месяц — {PRICES['month']}⭐\n"
        f"• Год — {PRICES['year']}⭐\n\n"
        f"Поддержка: {SUPPORT_USERNAME}",
        parse_mode='Markdown',
        reply_markup=keyboard
    )

@bot.callback_query_handler(func=lambda call: call.data == "buy")
def buy_callback(call):
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton("🔥 День (25⭐)", callback_data="pay_day"),
        InlineKeyboardButton("⚡ Неделя (100⭐)", callback_data="pay_week"),
        InlineKeyboardButton("🚀 Месяц (300⭐)", callback_data="pay_month"),
        InlineKeyboardButton("💎 Год (1500⭐)", callback_data="pay_year"),
        InlineKeyboardButton("◀️ Назад", callback_data="back")
    )
    bot.edit_message_text("💎 **ВЫБЕРИ ТАРИФ:**", call.message.chat.id, call.message.message_id, parse_mode='Markdown', reply_markup=keyboard)

@bot.callback_query_handler(func=lambda call: call.data.startswith('pay_'))
def pay_callback(call):
    plan = call.data.replace('pay_', '')
    price = PRICES.get(plan, 25)
    prices = [telebot.types.LabeledPrice(label=plan.capitalize(), amount=price * 100)]
    bot.send_invoice(
        call.message.chat.id,
        title=f"Подписка {plan.capitalize()}",
        description=f"Тариф: {plan.capitalize()}",
        invoice_payload=f"sub_{plan}_{call.from_user.id}",
        provider_token="",
        currency="XTR",
        prices=prices
    )

@bot.pre_checkout_query_handler(func=lambda q: True)
def pre_checkout(pre_checkout_query):
    bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)

@bot.message_handler(content_types=['successful_payment'])
def successful_payment(message):
    user_id = message.from_user.id
    payload = message.successful_payment.invoice_payload
    plan = payload.split('_')[1]
    code = generate_code(user_id)
    expiry = datetime.now() + timedelta(days={'day':1,'week':7,'month':30,'year':365}[plan])
    cursor.execute('''
        INSERT OR REPLACE INTO users (user_id, username, first_name, registered, code, plan, expiry)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (user_id, message.from_user.username, message.from_user.first_name, datetime.now(), code, plan, expiry))
    conn.commit()
    client_file = create_client_file(user_id, code, plan)
    with open(client_file, 'rb') as f:
        bot.send_document(user_id, f, caption="🔥 **ТВОЙ ГОТОВЫЙ ФАЙЛ!**\nСкопируй его на флешку.", parse_mode='Markdown')
    send_manual(user_id, code)
    bot.send_message(ADMIN_ID, f"💰 **ПРОДАЖА!**\n👤 Пользователь: {user_id}\n📆 Тариф: {plan}\n🎫 Код: {code}", parse_mode='Markdown')
    os.remove(client_file)

if __name__ == "__main__":
    print("="*60)
    print("🔥 MY TEST X - ОСНОВНОЙ БОТ")
    print("="*60)
    print("✅ Бот запущен!")
    print("="*60)
    bot.infinity_polling()
