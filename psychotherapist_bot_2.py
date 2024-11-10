from gpt4all import GPT4All
import telebot
import threading
import time
token = '7799653128:AAHm2-UnuX1iYwCJpgV1ZJPucJk8TJ1HnpU'

system_prompt = 'Ты Константин, психотерапевт. Пиши кратко. Пиши только на русском. Пиши не больше пары предложений.'

users = {}

bot = telebot.TeleBot(token)


@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_message = "Привет, кто ты?"
    if str(message.chat.id) not in users.keys():
        users[str(message.chat.id)] = welcome_message
        thread = threading.Thread(target=new_session, args = (message.chat.id, ))
        thread.start()
    else:
        users[str(message.chat.id)] = welcome_message

@bot.message_handler(commands=['stop'])
def stop_chat(message):
    users[str(message.chat.id)] = "stop"

@bot.message_handler(content_types=["text"])
def send_message(message): 
    if str(message.chat.id) in users.keys():
        users[str(message.chat.id)] = message.text
    else:
        users[str(message.chat.id)] = message.text
        thread = threading.Thread(target=new_session, args = (message.chat.id, ))
        thread.start()

def new_session(id):
    model = GPT4All("Meta-Llama-3-8B-Instruct.Q4_0.gguf", device='gpu')
    with model.chat_session(system_prompt=system_prompt):
        new_message = ""
        while True:
            time.sleep(1)
            if users[str(id)] == "stop":
                model.close()
                return
            if new_message != users[str(id)]:
                new_message = users[str(id)]
                bot.send_message(id, model.generate(new_message + " Ответь кратко, пара предложений"))

bot.infinity_polling()