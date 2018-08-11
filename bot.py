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
    'DAILY',
    'REST',
    'FOOD',
    'CARE',
    'HEALTH',
    'OTHER',
]

month_lst = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

month_dict = {'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6, 'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12}

month = []
shared_memory = {}
current_shown_dates = {}

@bot.message_handler(commands=['details'])
def details(message):
    if auth_users.count(int(message.from_user.id)):
        markup = types.ForceReply(selective=False)
        bot.send_message(message.chat.id, "Add description: \n "
                                          "Use . before your message".format(message.text), reply_markup=markup)

    else:
        bot.send_message(message.chat.id, 'Access denied')

@bot.message_handler(regexp='[.][a-zA-Z0-9]*')
def add_details(message):
    if auth_users.count(int(message.from_user.id)):
        gsheet.add_details(message.from_user.first_name, message.text)

    else:
        bot.send_message(message.chat.id, 'Access denied')


@bot.message_handler(commands=['remove'])
def del_last_record(message):
    if auth_users.count(int(message.from_user.id)):
       x = gsheet.delete_last_record(message.from_user.first_name)
       bot.send_message(message.chat.id, 'Last record was removed: \n{}: {}'.format(x[0][2], x[0][3]))
    else:
        bot.send_message(message.chat.id, 'Access denied')


@bot.message_handler(commands=['statistic'])
def period(message):
    if auth_users.count(int(message.from_user.id)):
        now = datetime.datetime.now()  # Current date
        chat_id = message.chat.id
        date = (now.year, now.month)
        current_shown_dates[chat_id] = date  # Saving the current date in a dict

        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(*[types.InlineKeyboardButton(text=name, callback_data=name) for name in ['DAY', 'MONTH']])
        bot.send_message(message.chat.id, 'Choose period:', reply_markup=keyboard)
    else:
        bot.send_message(message.chat.id, 'Access denied')


@bot.callback_query_handler(func=lambda call: call.data == 'DAY')
def my_calendar(call):
    now = datetime.datetime.now()
    chat_id = call.message.chat.id
    date = (now.year, now.month)
    current_shown_dates[chat_id] = date  # Saving the current date in a dict

    markup = create_calendar(now.year, now.month)
    bot.send_message(chat_id, "Please, choose a date", reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data == 'next-month')
def next_month(call):
    chat_id = call.message.chat.id
    saved_date = current_shown_dates.get(chat_id)
    if saved_date is not None:
        year, month = saved_date
        month += 1
        if month > 12:
            month = 1
            year += 1
        date = (year,month)
        current_shown_dates[chat_id] = date
        markup= create_calendar(year, month)
        bot.edit_message_text("Please, choose a date", call.from_user.id, call.message.message_id, reply_markup=markup)
        bot.answer_callback_query(call.id, text="")
    else:
        bot.send_message(chat_id, 'Date error. Please, try again')


@bot.callback_query_handler(func=lambda call: call.data == 'previous-month')
def previous_month(call):
    chat_id = call.message.chat.id
    saved_date = current_shown_dates.get(chat_id)
    if saved_date is not None:
        year, month = saved_date
        month -= 1
        if month < 1:
            month = 12
            year -= 1
        date = (year,month)
        current_shown_dates[chat_id] = date
        markup = create_calendar(year, month)
        bot.edit_message_text("Please, choose a date", call.from_user.id, call.message.message_id, reply_markup=markup)
        bot.answer_callback_query(call.id, text="")
    else:
        bot.send_message(chat_id, 'Date error. Please, try again')


@bot.callback_query_handler(func=lambda call: call.data[0:13] == 'calendar-day-')
def get_day(call):
    chat_id = call.message.chat.id
    saved_date = current_shown_dates.get(chat_id)
    if saved_date is not None:
        day = call.data[13:]
        choosen_date = datetime.date(int(saved_date[0]), int(saved_date[1]), int(day))
        bot.answer_callback_query(call.id, text="")
        shared_memory['choosen_date'] = call.message.text

        groups_of_costs = gsheet.find_data(call.message.chat.first_name, str(choosen_date))

        if groups_of_costs == {}:
            bot.send_message(chat_id, 'No record on this date')
        else:
            output = 'Total costs for {chosen_date}:\n'.format(chosen_date=choosen_date)
            for cost_type, amount in groups_of_costs.items():
                output += '   {cost_type}: {amount} UAH \n'.format(cost_type=cost_type, amount=amount)
            bot.send_message(chat_id, output)

    else:
        bot.send_message(chat_id, 'Date is null, try again')


@bot.callback_query_handler(func=lambda call: call.data == 'MONTH')
def get_month(call):
    for i in range(datetime.datetime.now().month - 3, datetime.datetime.now().month):
        month.append('▸ ' + month_lst[i])

    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(*[types.InlineKeyboardButton(
        text=name, callback_data=name) for name in month])
    bot.send_message(call.message.chat.id, 'Select month:', reply_markup=keyboard)



@bot.callback_query_handler(func=lambda call: call.data[0:2] == '▸ ')
def show_month_data(call):
    groups_of_costs = gsheet.find_month_data(call.message.chat.first_name, str(month_dict.get(call.data[2:])))

    if groups_of_costs == {}:
        bot.send_message(call.message.chat.id, 'No record on this date')
    else:
        output = 'Total costs for {chosen_date}:\n'.format(chosen_date=str(month_dict.get(call.data[2:])))
        for cost_type, amount in groups_of_costs.items():
            output += '   {cost_type}: {amount} UAH\n'.format(cost_type=cost_type, amount=amount)
        bot.send_message(call.message.chat.id, output)


@bot.message_handler(commands=['start'])
def start(message):
    if auth_users.count(int(message.from_user.id)):
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(*[types.InlineKeyboardButton(text=name, callback_data=name) for name in cost_lst])
        msg = bot.send_message(message.chat.id, 'Choose cost type:', reply_markup=keyboard)

    else:
        bot.send_message(message.chat.id, 'Access denied')


@bot.callback_query_handler(lambda query: True)
def on_inline_button_clicked(call):
    shared_memory['cost_type'] = call.data
    markup = types.ForceReply(selective=False)
    bot.send_message(call.message.chat.id, "Amount of {} is:".format(call.data), reply_markup=markup)


@bot.message_handler(content_types=["text"])
def func(message):
    user_name = message.from_user.first_name

    if auth_users.count(int(message.from_user.id)):
        try:
            int(message.text)
            cost_amount = message.text
            bot.send_message(message.chat.id, 'New record: \n{}: {} UAH'.format(
                shared_memory['cost_type'],
                cost_amount
            ))
            gsheet.add_to_sheet(user_name, shared_memory['cost_type'], cost_amount)

        except ValueError:
            bot.send_message(message.chat.id, 'Incorrect input. Please, use the following commands: \n'
                                              '/start - to record new data about expenses \n'
                                              '/statistic - to get information about previous expenses \n'
                                              '/remove - to remove last record \n'
                                              '/details - to add description to last record')
    else:
        bot.send_message(message.chat.id, 'Access denied')

bot.polling()




