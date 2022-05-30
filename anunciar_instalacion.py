from unicodedata import name
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import datetime
import pywhatkit 
import time

# Global variables of the spreadsheet.

scope = ["https://spreadsheets.google.com/feeds",'https://www.googleapis.com/auth/spreadsheets',"https://www.googleapis.com/auth/drive.file","https://www.googleapis.com/auth/drive"]

creds = ServiceAccountCredentials.from_json_keyfile_name("creds.json", scope)

client = gspread.authorize(creds)

spread_sheet = client.open("Mr.Mapeador EDDY") # Open the spreadhseet

sheet1 = spread_sheet.worksheet('Mr.Mapeador database')

sheet2 = spread_sheet.worksheet('Python variables')


tiendas_database= [
    ['Del Aire', 'IOSdH1NiiPdL6hG095SYT2','+51993548559','Jael','487'] 
]

def run_dr_merma(list_of_products_alerted):
    """
    Función principal: Envia los productos a vencer de cada tienda a sus respectivos grupos de wsp.
    En caso no halla productos a alertar, envia un mensaje avisandolo al grupo.
    Toma como párametro la nested-list generada en "enlist_products_to_alert()"
    """
    number_products_alerted = sheet2.cell(2,2).value
    number_products_maped = sheet2.cell(3,2).value
    for tienda in tiendas_database: # For loop para enviar los mensajes a cada tienda
        hour = int(time.strftime("%H"))
        if int(time.strftime("%S")) >= 51:
            minute = int(time.strftime("%M")) + 1
        else:
            minute = int(time.strftime("%M"))
        #Enlistar todos los nombres de productos por vencerse
        products_name = [list_of_products_alerted[i][1] for i in range(len(list_of_products_alerted)) if list_of_products_alerted[i][0] == tienda[4]]
        if products_name != []: #Si hay productos por vencerse, envia esto:
            products_name = "\n- ".join(products_name)
            print(products_name, "Enviando a ", tienda[0])
            ms1 = (f'Buenos dias {tienda[0]}, soy Dr. Merma\nEstadisticas hasta hoy:\n- {number_products_alerted} vencimientos alertados conmigo\n-{number_products_maped} vencimientos mapeados con Mr. Mapeador')
            ms2 = """Dr. Merma \U0001f468\u200D\u2695 recomienda revisar: \n""" +"- "+ products_name + '\nPara hoy ' + str((datetime.date.today()))
            print(ms2)
            pywhatkit.sendwhatmsg_to_group(tienda[1],ms1, hour, minute+1,11)
            pywhatkit.sendwhatmsg_to_group(tienda[1],ms2, hour, minute+2,11)
        else: #Si no hay productos por vencerse, envia esto:
            ms3 = f'Felicidades. Ningún vencimiento para {tienda[0]} el día {(datetime.date.today())}\n Que la pasen bien!'
            print(minute)
        
            pywhatkit.sendwhatmsg_to_group(tienda[1], ms3, hour, minute+1,11)
    # Enviar mensaje al admin.
    pywhatkit.sendwhatmsg(tiendas_database[0][2], f"""Felicidades administrador, Dr. Merma instalado""", 5, 50)

list_of_products_alerted = []
run_dr_merma(list_of_products_alerted)

