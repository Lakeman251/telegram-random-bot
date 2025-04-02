
from flask import Flask, request
import telebot
import os
import random
import threading
import time

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

# Короткий алиас для /рандом
@bot.message_handler(commands=['р'])
def handle_short_random(message):
    handle_random(message)

# Быстрые команды с фиксированным диапазоном
@bot.message_handler(commands=['из104'])
def handle_104(message):
    result = random.randint(1, 104)
    bot.reply_to(message, f"🎯 Твоё число от 1 до 104: {result}")

@bot.message_handler(commands=['из4'])
def handle_4(message):
    result = random.randint(1, 4)
    bot.reply_to(message, f"🎯 Твоё число от 1 до 4: {result}")

@bot.message_handler(commands=['из3'])
def handle_3(message):
    result = random.randint(1, 3)
    bot.reply_to(message, f"🎯 Твоё число от 1 до 3: {result}")

@bot.message_handler(commands=['из2'])
def handle_2(message):
    result = random.randint(1, 2)
    bot.reply_to(message, f"🎯 Твоё число от 1 до 2: {result}")

@bot.message_handler(commands=['к'])
def handle_commands_list(message):
    text = (
        "📋 *Команды бота:*\n"
        "/рандом A B — случайное число от A до B\n"
        "/р A B — то же самое, но короче\n"
        "/из104 — случайное число от 1 до 104\n"
        "/из4 — от 1 до 4\n"
        "/из3 — от 1 до 3\n"
        "/из2 — от 1 до 2\n"
        "/таймер N — таймер на N секунд (например: /таймер 120)\n"
        "/к — показать этот список команд"
    )
    bot.reply_to(message, text, parse_mode='Markdown')


@bot.message_handler(commands=['таймер'])
def start_timer(message):
    try:
        parts = message.text.split()
        seconds = int(parts[1])
        
        sent_message = bot.reply_to(message, f'⏳ Осталось: {seconds//60}:{seconds%60:02}')

        # Функция обновления таймера
        def update_timer(seconds_left, message_id, chat_id):
            while seconds_left > 0:
                minutes = seconds_left // 60
                seconds = seconds_left % 60
                bot.edit_message_text(
                    chat_id=chat_id,
                    message_id=message_id,
                    text=f'⏳ Осталось: {minutes}:{seconds:02}'
                )
                time.sleep(10)  # Обновляем раз в 10 секунд
                seconds_left -= 10
            
            # Когда таймер закончится
            bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text='⏳ Осталось: 0:00 🔔 Таймер окончен!'
            )

        # Запускаем таймер в отдельном потоке, чтобы не блокировать бота
        threading.Thread(
            target=update_timer,
            args=(seconds, sent_message.message_id, sent_message.chat.id)
        ).start()

    except Exception as e:
        bot.reply_to(message, 'Ошибка! Используй формат: /таймер 120 (в секундах)')

@app.route(f'/{TOKEN}', methods=['POST'])
def webhook():
    bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
    return '', 200

@app.route('/')
def index():
    return 'Бот работает!'

@app.route('/setwebhook')
def set_webhook():
    url = f'{os.environ.get("RENDER_EXTERNAL_URL")}/{TOKEN}'
    bot.remove_webhook()
    success = bot.set_webhook(url=url)
    if success:
        return '✅ Webhook установлен!'
    else:
        return '❌ Ошибка при установке webhook.'

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))
