# -*- coding: utf-8 -*-

# Importar módulos necesarios
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

spread_sheet = client.open("Mr.Mapeador database") # Open the spreadhseet

sheet1 = spread_sheet.worksheet('Mr.Mapeador database')

sheet2 = spread_sheet.worksheet('Python variables')

# Nested-list of all characteristics of each Mass minimarket (name,id_wsp_group, phone number of the admin,
# name of the admin, and minimarket's id)
tiendas_database= [
    ['Garzon 6', 'FTDFIE7D1P14BcNXz033we', '+51959260520','Shirel', '1162'],
    ['Garzon 11', 'IYflbYgMNltHzFJlpXrIlX', '+51946555502','Jubitza','831'],
    ['Del Aire', '', '+51935924465','Luz', '487']
] 

def enlist_products_to_alert():
    """
    Esta función extrae todos los productos que se van a vencer de la cuarta columna
    de la segunda spreadsheet, y retorna una nested-list con las características de vencimiento
    de cada producto.
    """
    minimarkets_of_products_not_alerted = (sheet2.col_values(3)) # Getting all "Tienda" numbers of all products.
    names_of_products_not_alerted = (sheet2.col_values(4)) # Getting all names of all products.
    daysleft_of_products_not_alerted = (sheet2.col_values(5)) # Getting all "days left"s value of all products.
    rownumber_of_products_not_alerted = (sheet2.col_values(6)) # Getting all row numbers of all products.
    list_of_products_not_alerted = [
                                    [
                                        minimarkets_of_products_not_alerted[i], # Getting "Tienda" number of each product
                                        names_of_products_not_alerted[i], # Getting the name of each product
                                        daysleft_of_products_not_alerted[i], # Getting "the days left" value of each product
                                        rownumber_of_products_not_alerted[i] # Getting the row number of each product
                                    ]
                                    for i in range(1,len(names_of_products_not_alerted))
                                    if ((minimarkets_of_products_not_alerted[i] == '831') or (int(daysleft_of_products_not_alerted[i]) < 4))
                                    # La tienda 831 es un caso especial debido a que hacen sus mermas por reglas de 5 días antes del vencimiento.
                                    # Justo el número máximo que acepta el query de celda C1 de la sheet2
                                ]
    print(list_of_products_not_alerted)
    return list_of_products_not_alerted

def change_alerted_status_of_product(list_of_products_alerted):
    """
    Esta función cambia el status de la columna "alert it?" de los productos ya alertados por Dr.Merma en
    la sheet1. Además aumenta +1 el número de "products alerted" en la celda B2 de la sheet2
    """
    rows_of_products_alerted = [list_of_products_alerted[i][3] for i in range(len(list_of_products_alerted))]

    for row_number in rows_of_products_alerted:
        cell = f"P{row_number}"
        sheet1.update(cell,"YES")
        contador = (int((sheet2.cell(2,2).value))) + 1
        cell = 'B2'
        sheet2.update(cell,contador)
        continue

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
        minute = int(time.strftime("%M")) + 1
        #Enlistar todos los nombres de productos por vencerse
        products_name = [list_of_products_alerted[i][1] for i in range(len(list_of_products_alerted)) if list_of_products_alerted[i][0] == tienda[4]]
        if products_name != []: #Si hay productos por vencerse, envia esto:
            products_name = "\n- ".join(products_name)
            print(products_name, "Enviando a ", tienda[0])
            ms2 = """Dr. Merma \U0001f468\u200D\u2695 recomienda revisar: \n""" +"- "+ products_name + '\nPara hoy ' + str((datetime.date.today()))
            ms1 = (f'Buenos dias {tienda[0]}, soy Dr. Merma.\n Estadísticas hasta hoy:\n- {number_products_alerted} vencimientos alertados.\n- Con Sr. Merma {number_products_maped} vencimientos mapeados.')
            print(ms2)
            if tienda[4] == '487': #La tienda 487 es un caso especial. No estoy en su grupo.
                pywhatkit.sendwhatmsg(tienda[2],ms1, hour, minute+1,18)
                pywhatkit.sendwhatmsg(tienda[2],ms2, hour, minute+2,18)
                continue
            pywhatkit.sendwhatmsg_to_group(tienda[1],ms1, hour, minute+1,18)
            pywhatkit.sendwhatmsg_to_group(tienda[1],ms2, hour, minute+2,18)
        else: #Si no hay productos por vencerse, envia esto:
            ms3 = f'Felicidades. Ningún vencimiento para {tienda[0]} el día {(datetime.date.today())}\n Que la pasen bien!'
            if tienda[4] == '487': #La tienda 487 es un caso especial. No estoy en su grupo.
                pywhatkit.sendwhatmsg(tienda[2], ms3, hour, minute+1,18)
                continue
            pywhatkit.sendwhatmsg_to_group(tienda[1], ms3, hour, minute+1,18)

def avisar_admins_consolidado():
    """
    Función para avisar a las admins de cada tienda que mapeen vencimientos del siguiente mes
    """
    for tienda in tiendas_database:
        hour = int(time.strftime("%H"))
        minute = int(time.strftime("%M")) + 1
        pywhatkit.sendwhatmsg(tienda[2], f"""Hola {tienda[3]}. Soy Dr.Merma. Hoy es 28, se recomienda empezar el mapeo de vencimientos del siguiente mes""", hour, minute+1)

def avisar_actualizar_data():
    """
    Función para avisar a los admins que actualizen el Listado de stock por ser viernes (Cambio de precios).
    """
    for tienda in tiendas_database:
        hour = int(time.strftime("%H"))
        minute = int(time.strftime("%M")) + 1
        pywhatkit.sendwhatmsg(tienda[2], f"""Hola {tienda[3]}. Soy Dr.Merma. Hoy es viernes, te recomiendo actualizar tu listado de stock por el cambio de precio \nLo encuentras el excel de Mr.Mapeador en "Data + Número de tienda" """, hour, minute+1)

def enlist_products_errors():
    """
    Esta función extrae todos los productos que tienen un valor unitario de 0 y retorna una nested-list
    con el nombre de este producto y en qué columnas se encuentran.
    Esto porque no tiene sentido. ¿Cómo vas a mapear un producto que, según tu inventario, no tienes?
    """
    minimarkets_of_products_with_error = (sheet2.col_values(8)) # Getting all "Tienda" numbers of all products.
    names_of_products_with_error = (sheet2.col_values(9)) # Getting all names of all products.
    rownumber_of_products_with_error = (sheet2.col_values(10)) # Getting all row numbers of all products.
    list_of_products_with_error = [
                                    [
                                        minimarkets_of_products_with_error[i], # Getting "Tienda" number of each product
                                        names_of_products_with_error[i], # Getting the name of each product
                                        rownumber_of_products_with_error[i] # Getting the row number of each product
                                    ]
                                    for i in range(1,len(minimarkets_of_products_with_error))
                                ]
    print(list_of_products_with_error)
    return list_of_products_with_error

def change_alerted_status_error(list_of_products_errors):
    """
    Esta función cambia el status de la columna "Error alertado" de los errores ya alertados por Dr.Errors en
    la sheet1.
    """
    rows_of_errors_alerted = [list_of_products_errors[i][2] for i in range(len(list_of_products_errors))]

    for row_number in rows_of_errors_alerted:
        cell = f"S{row_number}"
        sheet1.update(cell,"YES")
        continue

def run_dr_errors(list_of_products_errors):
    """
    Función principal: Envia los productos a vencer de cada tienda a sus respectivos grupos de wsp.
    En caso no halla productos a alertar, envia un mensaje avisandolo al grupo.
    Toma como párametro la nested-list generada en "enlist_products_to_alert()"
    """
    for tienda in tiendas_database: # For loop para enviar los mensajes a cada tienda
        hour = int(time.strftime("%H"))
        minute = int(time.strftime("%M")) + 1
        #Enlistar todos los nombres de productos por vencerse
        products_name = [list_of_products_errors[i][1] for i in range(len(list_of_products_errors)) if list_of_products_errors[i][0] == tienda[4]]
        rows_products = [list_of_products_errors[i][2] for i in range(len(list_of_products_errors)) if list_of_products_errors[i][0] == tienda[4]]
        if products_name != []: #Si hay productos con errores, envia esto:
            name_and_row_products = [(f"{products_name[i]} en la fila {rows_products[i]}") for i in range(len(rows_products))]
            products_name = "\n- ".join(name_and_row_products)
            print(products_name, "Enviando a ", tienda[0])
            ms1 = """Estos productos salieron con error: \n""" +"- "+ products_name + '\n Se recomienda revisar porque en el listado aparecen como si tuvieran 0'
            print(ms1)
            if tienda[4] == '487': #La tienda 487 es un caso especial. No estoy en su grupo.
                pywhatkit.sendwhatmsg(tienda[2],ms1, hour, minute+1,18)
                continue
            pywhatkit.sendwhatmsg_to_group(tienda[1],ms1, hour, minute+1,18)
        else: #Si no hay productos con errores, envia esto:
            continue

def run():
    print("Empezando programa")
    list_exp_products = enlist_products_to_alert()
    print("Productos enlistados con exito")
    run_dr_merma(list_exp_products)
    print("Mensajes enviados")
    change_alerted_status_of_product(list_exp_products)
    print("Productos status cambiados")
    print("Revisar si hay productos con errores")
    list_products_errs = enlist_products_errors()
    if list_products_errs != []:
        run_dr_errors(list_products_errs)
        print("Errores enviados")
        change_alerted_status_error(list_products_errs)
        print("Errores status cambiados")
    todays_number = int(time.strftime("%d"))
    name_of_today = time.strftime("%A")
    if name_of_today == 'Friday':
        print("Avisando a los admin para actualizar el listado de stock")
        avisar_actualizar_data()
    if todays_number == 28:
        print('Avisando a admins para mapear los proximos a vencer')
        avisar_admins_consolidado()
    print("Programa Finalizado")

if __name__ == '__main__':
    run()
    print("""
----------------------------------------------------------""")  
