# -*- coding: utf-8 -*-
# import config
import os
import telebot
from telebot import types
import gsheet

#bot = telebot.TeleBot(config.token)
bot = telebot.TeleBot(os.environ['telegram_token'])
auth_users = [445219449, 394294378]

cost_lst = [
    'cost 1',
    'cost 2',
    'cost 3',
    'cost 4',
    'other',
]

shared_memory = {}


@bot.message_handler(commands=['start'])
def start(message):
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(*[types.InlineKeyboardButton(text=name, callback_data=name) for name in cost_lst])
    bot.send_message(message.chat.id, 'Choose cost type:', reply_markup=keyboard)
    shared_memory['chat_id'] = message.chat.id


@bot.callback_query_handler(lambda query: True)
def on_inline_button_clicked(call):
    shared_memory['cost_type'] = call.data
    markup = types.ForceReply(selective=False)
    bot.send_message(shared_memory['chat_id'], "Amount of {} is:".format(call.data), reply_markup=markup)


@bot.message_handler(content_types=["text"])
def func(message):
    user_name = message.from_user.first_name
    if auth_users.count(int(message.from_user.id)):
        try:
            int(message.text)
            shared_memory['cost_amount'] = message.text
            bot.send_message(message.chat.id, 'Cost type is: {}, amount is {}'.format(
                shared_memory['cost_type'],
                shared_memory['cost_amount'])
                             )
            gsheet.add_to_sheet(user_name, shared_memory['cost_type'], shared_memory['cost_amount'])
        except ValueError as v:
            bot.send_message(message.chat.id, 'Incorrect input {}'.format(v))
    else:
        bot.send_message(message.chat.id, 'Access denied')


bot.polling()