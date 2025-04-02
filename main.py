
from flask import Flask, request
import telebot
import os
import random

TOKEN = os.environ.get('TELEGRAM_TOKEN')
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "Привет! Напиши /рандом 1 100, чтобы получить случайное число.")

@bot.message_handler(commands=['рандом'])
def handle_random(message):
    try:
        parts = message.text.split()
        if len(parts) != 3:
            bot.reply_to(message, "Формат: /рандом 1 100")
            return
        a, b = int(parts[1]), int(parts[2])
        result = random.randint(min(a, b), max(a, b))
        bot.reply_to(message, f"🎲 Твоё число: {result}")
    except:
        bot.reply_to(message, "Ошибка! Используй формат: /рандом 1 100")

@app.route(f'/{TOKEN}', methods=['POST'])
def webhook():
    bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
    return '', 200

@app.route('/')
def index():
    return 'Бот работает!'

@app.before_request
def activate_webhook():
    bot.remove_webhook()
    bot.set_webhook(url=f'{os.environ.get("RENDER_EXTERNAL_URL")}/{TOKEN}')

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))
