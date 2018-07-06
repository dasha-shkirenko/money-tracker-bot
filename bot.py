# -*- coding: utf-8 -*-
# import config
import os
import telebot
from telebot import types
import gsheet
from telegramcalendar import create_calendar
import datetime

# bot = telebot.TeleBot(config.token)
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
current_shown_dates = {}

@bot.message_handler(commands=['statistic'])
def calendar(message):
    now = datetime.datetime.now()  # Current date
    chat_id = message.chat.id
    date = (now.year, now.month)
    current_shown_dates[chat_id] = date  # Saving the current date in a dict
    markup = create_calendar(now.year, now.month)
    bot.send_message(message.chat.id, "Please, choose a date", reply_markup=markup)

    shared_memory['chat_id'] = message.chat.id
    shared_memory['user_first_name'] = message.from_user.first_name


@bot.callback_query_handler(func=lambda call: call.data == 'next-month')
def next_month(call):
    chat_id = call.message.chat.id
    saved_date = current_shown_dates.get(chat_id)
    if(saved_date is not None):
        year,month = saved_date
        month+=1
        if month>12:
            month=1
            year+=1
        date = (year,month)
        current_shown_dates[chat_id] = date
        markup= create_calendar(year,month)
        bot.edit_message_text("Please, choose a date", call.from_user.id, call.message.message_id, reply_markup=markup)
        bot.answer_callback_query(call.id, text="")
    else:
        #Do something to inform of the error
        pass

@bot.callback_query_handler(func=lambda call: call.data == 'previous-month')
def previous_month(call):
    chat_id = call.message.chat.id
    saved_date = current_shown_dates.get(chat_id)
    if(saved_date is not None):
        year,month = saved_date
        month-=1
        if month<1:
            month=12
            year-=1
        date = (year,month)
        current_shown_dates[chat_id] = date
        markup= create_calendar(year,month)
        bot.edit_message_text("Please, choose a date", call.from_user.id, call.message.message_id, reply_markup=markup)
        bot.answer_callback_query(call.id, text="")
    else:
        pass


@bot.callback_query_handler(func=lambda call: call.data[0:13] == 'calendar-day-')
def get_day(call):
    chat_id = call.message.chat.id
    saved_date = current_shown_dates.get(chat_id)
    if(saved_date is not None):
        day = call.data[13:]
        choosen_date = datetime.date(int(saved_date[0]),int(saved_date[1]),int(day))
        # bot.send_message(chat_id, str(choosen_date))
        bot.answer_callback_query(call.id, text="")
        shared_memory['choosen_date'] = call.message.text

        print(choosen_date)
        cost_amount = gsheet.find_data(shared_memory['user_first_name'], str(choosen_date))
        bot.send_message(chat_id, 'Date: {}, amount of costs: {}'.format(choosen_date, cost_amount))

    else:
        pass




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
            bot.send_message(message.chat.id, 'Cost type is {}, amount is {}'.format(
                shared_memory['cost_type'],
                shared_memory['cost_amount'])
                             )
            gsheet.add_to_sheet(user_name, shared_memory['cost_type'], shared_memory['cost_amount'])
        except ValueError as v:
            bot.send_message(message.chat.id, 'Incorrect input {}'.format(v))
    else:
        bot.send_message(message.chat.id, 'Access denied')



bot.polling()