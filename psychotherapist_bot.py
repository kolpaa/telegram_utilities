from g4f.client import Client
import telebot

psychotherapist_bot = Client()
proofreader = Client()
token = '7799653128:AAHm2-UnuX1iYwCJpgV1ZJPucJk8TJ1HnpU'

proofreader_system_promt = [{"role": "system", "content": 
              "Russian language. Your job is proofreader. Yoy are a proofreader. Correct text. You speak only Russian. Only Russian language. Russian language"}]
psychotherapist_system_promt = [{"role": "system", "content": 
              "Your job is psychotherapist. Yoy are a psychotherapist. Act as a psychotherapist. Your name is Konstantin, You speak only Russian. Only Russian language"}]

proofreader_messages = {}
psychotherapist_messages = {}


def request_processing(message, id):
    if message:
        if id not in psychotherapist_messages.keys():
            psychotherapist_messages[id] = psychotherapist_system_promt
            proofreader_messages[id] = proofreader_system_promt
            
        psychotherapist_messages[id].append(
            {"role": "user", "content": message},
        )
        chat = psychotherapist_bot.chat.completions.create(
            model= "gpt-3.5-turbo", messages=psychotherapist_messages[id]
        )
    if chat.choices[0].message.content.startswith('Model'):
        return False
    else:
        return chat.choices[0].message.content


def correct_message(message, id):
     if message:
        proofreader_messages[id].append(
            {"role": "user", "content": f"Correct message and send result, only russian language: {message}"},
        )
        chat = psychotherapist_bot.chat.completions.create(
            model="gpt-3.5-turbo", messages=proofreader_messages[id]
        )
        del proofreader_messages[id][-1]
     if chat.choices[0].message.content.startswith('Model'):
        return False
     else:
        return chat.choices[0].message.content


bot = telebot.TeleBot(token)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_string = f"Name: {message.from_user.first_name}, Добрый день! Кто вы?"
    reply = request_processing(welcome_string, message.chat.id)
    while not reply:
        reply = request_processing(welcome_string, message.chat.id)
    bot.send_message(message.chat.id, reply)
    psychotherapist_messages[message.chat.id].append({"role": "assistant", "content": reply})


@bot.message_handler(commands=['stop'])
def send_bye(message):
    reply = request_processing(f"Name: {message.from_user.first_name}, Пока!", message.chat.id)
    while not reply:
        reply = request_processing(f"Name: {message.from_user.first_name}, Пока", message.chat.id)
    bot.send_message(message.chat.id, reply)
    psychotherapist_messages[message.chat.id].append({"role": "assistant", "content": reply})


@bot.message_handler(content_types=["text"])
def send_message(message): 
    print(psychotherapist_messages)
    reply = request_processing(message.text, message.chat.id)
    while not reply:
        reply = request_processing(message.text, message.chat.id)

    corrected_reply = correct_message(reply, message.chat.id)
    while not corrected_reply:
         corrected_reply = correct_message(reply, message.chat.id)

    bot.send_message(message.chat.id, corrected_reply)
    psychotherapist_messages[message.chat.id].append({"role": "assistant", "content": corrected_reply})

if __name__ == '__main__':
     bot.infinity_polling()



