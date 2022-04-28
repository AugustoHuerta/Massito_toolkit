from unicodedata import name
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from pprint import pprint
import datetime
from datetime import date
import pywhatkit 
import time
import pyautogui

# Global variables

scope = ["https://spreadsheets.google.com/feeds",'https://www.googleapis.com/auth/spreadsheets',"https://www.googleapis.com/auth/drive.file","https://www.googleapis.com/auth/drive"]

creds = ServiceAccountCredentials.from_json_keyfile_name("creds.json", scope)

client = gspread.authorize(creds)

spread_sheet = client.open("Massito") # Open the spreadhseet

sheet1 = spread_sheet.worksheet('Mr.Mapeador database')

sheet2 = spread_sheet.worksheet('Python variables')

sheet3 = spread_sheet.worksheet('DataJst')

currenthour = int(time.strftime("%H"))
currentminute = int(time.strftime("%M"))
todays_number = int("".join(list(time.strftime("%D"))[3:5]))

def enlist_products_not_alerted():
    list_of_products_not_alerted = sheet2.col_values(4)
    list_of_products_not_alerted.pop(0)
    print(list_of_products_not_alerted)
    return list_of_products_not_alerted

def change_alerted_value_of_product():
    list_of_index_products_alerted = sheet2.col_values(8)
    list_of_index_products_alerted.pop(0)
    for row_number in list_of_index_products_alerted:
        cell = f'O{row_number}'
        sheet1.update(cell,"YES")
        contador = (int((sheet2.cell(2,2).value))) + 1
        cell = 'B2'
        sheet2.update(cell,contador)
        continue

def dr_merma(list_exp_products, hour, minute):
    products = "\n- ".join(list_exp_products)
    print(products)
    number_products_alerted = sheet2.cell(2,2).value
    number_products_maped = sheet2.cell(3,2).value
    ms1 = """Dr. Merma \U0001f468\u200D\u2695 recomienda revisar: \n""" +"- "+ products + '\nPara hoy ' + str((date.today()))
    ms2 = (f'Hasta hoy he alertado {number_products_alerted} vencimientos y Sr. Merma mapeado {number_products_maped} productos.')
    ms3 = (f"Turno 1 Responda este mensaje confirmando la informacion recibida, por favor.")
    print(ms1)
    pywhatkit.sendwhatmsg_to_group('FTDFIE7D1P14BcNXz033we',ms3, hour, minute,18)
    pywhatkit.sendwhatmsg_to_group('FTDFIE7D1P14BcNXz033we',ms1, hour, minute+1,18)
    pywhatkit.sendwhatmsg_to_group('FTDFIE7D1P14BcNXz033we',ms2, hour, minute+2,18) 
    # pywhatkit.sendwhatmsg("+51918234518", "Dr. Merma \U0001f468\u200D\u2695 recomienda revisar: " + products + ', para hoy ' + str((date.today())), hour, minute,15)

def run(hour,minute):
    list_exp_products = enlist_products_not_alerted()
    if list_exp_products != []:
        #dr_merma(list_exp_products,hour,minute)
        change_alerted_value_of_product()
    else:
        number_products_alerted = sheet2.cell(2,2).value
        number_products_maped = sheet2.cell(3,2).value
        print('Not bad products founded')
        pywhatkit.sendwhatmsg_to_group('FTDFIE7D1P14BcNXz033we',"Dr. Merma no ha encontrado malos vencimientos para hoy " + str((date.today())), hour, minute,18)
        pywhatkit.sendwhatmsg_to_group('FTDFIE7D1P14BcNXz033we',(f'Hasta hoy he alertado {number_products_alerted} vencimientos y Sr. Merma mapeado {number_products_maped} productos.'), hour, minute+1,18)
        pywhatkit.sendwhatmsg_to_group('FTDFIE7D1P14BcNXz033we',(f'Me despido de turno 1'), hour, minute+2,18)

if __name__ == '__main__':
    run(6,0)
    # run(currenthour,currentminute+1)
    if todays_number == 28:
        pywhatkit.sendwhatmsg("+51935924465", "Hola Luz. Soy Dr.Merma. Te recomiendo iniciar el proceso de mapeo de fechas para el siguiente mes, ya que estamos 28", 6, 20,18)