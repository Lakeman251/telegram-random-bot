
from flask import Flask, request
import telebot
import os
import random
import threading
import time

# глобальная переменная: интервал обновления таймера (по умолчанию 20 секунд)
update_interval = 20

TOKEN = os.environ.get('TELEGRAM_TOKEN')
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# Разрешённые ID: супергруппа и личка
ALLOWED_CHAT_IDS = [-1002523843565, 491842357]

def is_allowed(message):
    if message.chat.id not in ALLOWED_CHAT_IDS:
        bot.send_message(
            message.chat.id,
            "❌ Извините, бот доступен только в отдельных чатах.",
            reply_to_message_id=message.message_id
        )
        return False
    return True

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    if not is_allowed(message): return
    bot.reply_to(message, "Привет! Напиши /рандом 1 100, чтобы получить случайное число.")

@bot.message_handler(commands=['рандом'])
def handle_random(message):
    if not is_allowed(message): return
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

@bot.message_handler(commands=['р'])
def handle_short_random(message):
    if not is_allowed(message): return
    handle_random(message)

@bot.message_handler(commands=['из104'])
def handle_104(message):
    if not is_allowed(message): return
    result = random.randint(1, 104)
    bot.reply_to(message, f"🎯 Твоё число от 1 до 104: {result}")

@bot.message_handler(commands=['из4'])
def handle_4(message):
    if not is_allowed(message): return
    result = random.randint(1, 4)
    bot.reply_to(message, f"🎯 Твоё число от 1 до 4: {result}")

@bot.message_handler(commands=['из3'])
def handle_3(message):
    if not is_allowed(message): return
    result = random.randint(1, 3)
    bot.reply_to(message, f"🎯 Твоё число от 1 до 3: {result}")

@bot.message_handler(commands=['из2'])
def handle_2(message):
    if not is_allowed(message): return
    result = random.randint(1, 2)
    bot.reply_to(message, f"🎯 Твоё число от 1 до 2: {result}")

@bot.message_handler(commands=['к'])
def handle_commands_list(message):
    if not is_allowed(message): return
    text = (
    "📋 *Команды бота:*\n\n"
    "🎲 *Рандомные числа:*\n"
    "/рандом A B — случайное число от A до B\n"
    "/р A B — то же самое, но короче\n"
    "/из104 — случайное число от 1 до 104\n"
    "/из4 — от 1 до 4\n"
    "/из3 — от 1 до 3\n"
    "/из2 — от 1 до 2\n\n"
    "⏱ *Таймеры:*\n"
    "/таймер N — таймер на N секунд (например: /таймер 120)\n"
    "/обновление N — установить интервал обновления таймера (в секундах, до 1 часа)\n\n"
    "🧾 *Прочее:*\n"
    "/к — показать этот список команд"
    )
    bot.reply_to(message, text, parse_mode='Markdown')

@bot.message_handler(commands=['обновление'])
def set_update_interval(message):
    if not is_allowed(message): return
    global update_interval
    try:
        parts = message.text.split()
        seconds = int(parts[1])
        if seconds < 5 or seconds > 3600:
            bot.reply_to(message, "⚠️ Интервал должен быть от 5 до 3600 секунд.")
            return
        update_interval = seconds
        bot.reply_to(message, f"✅ Интервал обновления установлен: каждые {seconds} сек.")
    except:
        bot.reply_to(message, "⚠️ Формат: /обновление 15 — число в секундах.")

@bot.message_handler(commands=['таймер'])
def start_timer(message):
    if not is_allowed(message): return
    try:
        parts = message.text.split()
        if len(parts) != 2 or not parts[1].isdigit():
            raise ValueError

        seconds = int(parts[1])
        if seconds < 1:
            bot.reply_to(message, "⚠️ Введи число больше 0.")
            return

        chat_id = message.chat.id
        thread_id = message.message_thread_id

        bot.send_message(
            chat_id,
            f'⏳ Осталось: {seconds // 60}:{seconds % 60:02}',
            message_thread_id=thread_id
        )

        def run_timer(total_seconds, chat_id, thread_id):
            global update_interval
            while total_seconds > 0:
                sleep_time = min(update_interval, total_seconds)
                time.sleep(sleep_time)
                total_seconds -= sleep_time
                if total_seconds > 0:
                    bot.send_message(
                        chat_id,
                        f'⏳ Осталось: {total_seconds // 60}:{total_seconds % 60:02}',
                        message_thread_id=thread_id
                    )
            bot.send_message(chat_id, '🔔 Таймер окончен!', message_thread_id=thread_id)

        threading.Thread(
            target=run_timer,
            args=(seconds, chat_id, thread_id)
        ).start()

    except:
        bot.reply_to(message, '⚠️ Используй формат: /таймер 60')

@bot.message_handler(commands=['id'])
def get_chat_id(message):
    bot.reply_to(message, f"🆔 chat.id: `{message.chat.id}`", parse_mode='Markdown')

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
