import datetime
import re
import gspread
import os
from oauth2client.service_account import ServiceAccountCredentials
from itertools import groupby


scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']

# credentials = ServiceAccountCredentials.from_json_keyfile_name('Money Tracker Bot-a66bfffca502.json', scope)
credentials.prigotvvate_key = os.environ['private_key']
credentials.private_key_id = os.environ['private_key_id']

open_file = gspread.authorize(credentials).open('MoneyTrackerBot')

record_date = str(datetime.datetime.now().strftime("%Y-%m-%d"))
record_time = str(datetime.datetime.now().strftime("%H:%M"))


def add_to_sheet(user_name, cost_type, cost_amount):
    try:
        open_file.worksheet(user_name).append_row(
            [record_date, record_time, cost_type, cost_amount]
        )
    except:
        open_file.add_worksheet(title=user_name, rows=100, cols=20)
        open_file.worksheet(user_name).append_row(
            [record_date, record_time, cost_type, cost_amount]
        )
def find_data(user_name, choosen_date):
    rd = open_file.worksheet(user_name).findall(choosen_date)
    rows = []
    group_to_sum = {}
    cost_group = ''

    for i in rd:
        rows.append(open_file.worksheet(user_name).row_values(i.row))

    sorted_data = sorted(rows, key=lambda item: item[2])

    for key, group in groupby(sorted_data, lambda x: x[2]):
        cost_group = key
        group_to_sum[key] = 0
        for value in group:
            group_to_sum[key] += int(value[3])

    return group_to_sum


def find_month_data(user_name, choosen_month):
    rows = []
    rd = open_file.worksheet(user_name).findall(choosen_month)
    group_to_sum = {}
    cost_group = ''

    if int(choosen_month) < 10:
        choosen_month = '0' + choosen_month

        criteria_re = re.compile(r'^{year}-{choosen_month}'.format(year=2018, choosen_month=choosen_month))
        cell_list = open_file.worksheet(user_name).findall(criteria_re)

        for i in cell_list:
            rows.append(open_file.worksheet(user_name).row_values(i.row))

        sorted_data = sorted(rows, key=lambda item: item[2])

        for key, group in groupby(sorted_data, lambda x: x[2]):
            cost_group = key
            group_to_sum[key] = 0
            for value in group:
                group_to_sum[key] += int(value[3])

        return group_to_sum


def delete_last_record(user_name):
   rc = open_file.worksheet(user_name).row_count
   last_record = open_file.worksheet(user_name).row_values(rc)
   dlr = open_file.worksheet(user_name).delete_row(rc)

   return last_record, dlr


def add_details(user_name, detail_text):
    rc = open_file.worksheet(user_name).row_count
    last_record = open_file.worksheet(user_name).row_values(rc)
    edit_lr = open_file.worksheet(user_name).update_cell(rc, 5, detail_text)

    return edit_lr

