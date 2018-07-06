import datetime
import gspread
import os
from oauth2client.service_account import ServiceAccountCredentials

scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']

credentials = ServiceAccountCredentials.from_json_keyfile_name('Money Tracker Bot-a66bfffca502.json', scope)
credentials.private_key = os.environ['private_key']
credentials.private_key_id = os.environ['private_key_id']

open_file = gspread.authorize(credentials).open('MoneyTrackerBot')

record_date = str(datetime.datetime.now().strftime("%Y-%m-%d"))
record_time = str(datetime.datetime.now().strftime("%H:%M"))


def user_check(user_id):
    print(user_id)


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

    for i in rd:
        rows.append(open_file.worksheet(user_name).row_values(i.row))

    total_cost_amount = sum([int(row[3]) for row in rows])
    return total_cost_amount






