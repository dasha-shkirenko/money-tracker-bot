import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials

scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']

credentials = ServiceAccountCredentials.from_json_keyfile_name('Money Tracker Bot-a66bfffca502.json', scope)

gc = gspread.authorize(credentials)

wks1 = gc.open('MoneyTrackerBot').worksheet('Dasha')
wks2 = gc.open('MoneyTrackerBot').worksheet('Dima')

record_date = str(datetime.datetime.now().strftime("%m-%d-%Y"))
record_time = str(datetime.datetime.now().strftime("%H:%M"))


def add_to_sheet(user, cost_type, cost_amount):
    wks1.append_row([user, record_date, record_time, cost_type, cost_amount])