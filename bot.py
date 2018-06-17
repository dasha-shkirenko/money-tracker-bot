# -*- coding: utf-8 -*-
import config
import telebot
from telebot import types


bot = telebot.TeleBot(config.token)

auth_users = [445219449, 394294378]
cost_lst = ['Choise 1', 'Choise 2', 'Choise 3', 'Choise 4']
cost_dict = {'Choise 1': 'answer 1', 'Choise 2': 'answer 2', 'Choise 3': 'answer 3', 'Choise 4': 'answer 4'}

@bot.message_handler(commands=['start'])

def start(message):
	if message.from_user.id == 445219449 or message.from_user.id == 394294378:
		bot.reply_to(message, 'Come in')
	else:
		bot.reply_to(message, 'sorry')

	keyboard = types.InlineKeyboardMarkup()
	keyboard.add(*[types.InlineKeyboardButton(text=name, callback_data = name) for name in cost_lst])
	msg = bot.send_message(message.chat.id, 'What is your choise?', reply_markup=keyboard)


@bot.message_handler(content_types=["text"])
def func(message): 
    bot.send_message(message.chat.id, 'Make a choice')




bot.polling()