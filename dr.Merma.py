# -*- coding: utf-8 -*-

# Importar módulos necesarios
from unicodedata import name
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import datetime
import pywhatkit 
import time
from functools import reduce 

# Global variables of the spreadsheet.

scope = ["https://spreadsheets.google.com/feeds",'https://www.googleapis.com/auth/spreadsheets',"https://www.googleapis.com/auth/drive.file","https://www.googleapis.com/auth/drive"]

creds = ServiceAccountCredentials.from_json_keyfile_name("creds.json", scope)

client = gspread.authorize(creds)

spread_sheets  = (
    client.open('Mr.Mapeador EDDY'),
    client.open('Mr.Mapeador LUIS')
)

sheets = {
    'Mr. Mapeadores sheets' : [spread_sheet.worksheet('Mr.Mapeador database') for spread_sheet in spread_sheets],
    'Python variables sheets' : [spread_sheet.worksheet('Python variables') for spread_sheet in spread_sheets]
}

# Nested-list of all characteristics of each Mass minimarket (name,id_wsp_group, phone number of the admin,
# name of the admin, and minimarket's id)
tiendas_database= [
    ['Garzon 6', 'FTDFIE7D1P14BcNXz033we', '+51959260520','Shirel', '1162'],
    ['Garzon 11', 'IYflbYgMNltHzFJlpXrIlX', '+51946555502','Jubitza','831'],
    ['Del Aire', 'IOSdH1NiiPdL6hG095SYT2','+51935924465','Luz','487'],
    ['Larra', 'KZbZ8dKu7Qr2Yu7poBwGs6', '+51953701471','Katheryne', '762'],
    ['Luzuriaga', '','+51951146921','Diego','569'],
    ['Miller', 'HPEv9MC73SkG3QwXyFdj0h','+51993931299','Jorge','745']
] 

def enlist_products_to_alert():
    """
    Esta función extrae todos los productos que se van a vencer de la cuarta columna
    de la segunda spreadsheet, y retorna una nested-list con las características de vencimiento
    de cada producto.
    """
    try:
        minimarkets_of_products_not_alerted = [value for sheet in sheets['Python variables sheets'] for value in sheet.col_values(3)[1:]] # Getting all "Tienda" numbers of all products.
        names_of_products_not_alerted = [value for sheet in sheets['Python variables sheets'] for value in sheet.col_values(4)[1:]] # Getting all names of all products.
        daysleft_of_products_not_alerted = [value for sheet in sheets['Python variables sheets'] for value in sheet.col_values(5)[1:]] # Getting all "days left"s value of all products.
        rownumber_of_products_not_alerted = [value for sheet in sheets['Python variables sheets'] for value in sheet.col_values(6)[1:]] # Getting all row numbers of all products.
        coordinador = [value for sheet in sheets['Python variables sheets'] for value in sheet.col_values(7)[1:]] # Getting name of coordi.
        list_of_products_not_alerted = [
                                        [
                                            minimarkets_of_products_not_alerted[i], # Getting "Tienda" number of each product
                                            names_of_products_not_alerted[i], # Getting the name of each product
                                            daysleft_of_products_not_alerted[i], # Getting "the days left" value of each product
                                            rownumber_of_products_not_alerted[i], # Getting the row number of each product
                                            coordinador[i] # Getting the name of coordi (So the program can differentiatiate among sheets)
                                        ]
                                        for i in range(len(names_of_products_not_alerted))
                                        if ( (minimarkets_of_products_not_alerted[i] != '1162') or (int(daysleft_of_products_not_alerted[i]) < -1) )
                                        # La tienda 1162 es un caso especial debido a que hacen sus mermas por reglas de 3 días antes del vencimiento.
                                    ]
    except Exception as error:
        print("Sucedió un error al enlistar productos por vencer")
        print(error)
        return []
    if list_of_products_not_alerted == []:
        print("Terminado. No se encontró productos por vencerse")
    else:
        print("Terminado. Productos por vencerse enlistados")
        print(list_of_products_not_alerted)
    return list_of_products_not_alerted

def enlist_15_days_products():
    """
    Esta función extrae todos los productos que no van a venderse en 15 dias y retorna una nested-list
    con el nombre de este producto y en qué columnas se encuentran.
    Esto para que los admins puedan hacer traslasdo de esos productos antes
    """
    try:
        minimarkets_of_products_with_error = [value for sheet in sheets['Python variables sheets'] for value in sheet.col_values(12)[1:]] # Getting all "Tienda" numbers of all products.
        names_of_products_with_error = [value for sheet in sheets['Python variables sheets'] for value in sheet.col_values(13)[1:]] # Getting all names of all products.
        rownumber_of_products_with_error = [value for sheet in sheets['Python variables sheets'] for value in sheet.col_values(14)[1:]] # Getting all row numbers of all products.
        coordinador = [value for sheet in sheets['Python variables sheets'] for value in sheet.col_values(15)[1:]] # Getting name of coordi.
        list_of_products_with_error = [
                                        [
                                            minimarkets_of_products_with_error[i], # Getting "Tienda" number of each product
                                            names_of_products_with_error[i], # Getting the name of each product
                                            rownumber_of_products_with_error[i], # Getting the row number of each product
                                            coordinador[i] # Getting the name of coordi (So the program can differentiatiate among sheets)
                                        ]
                                        for i in range(len(minimarkets_of_products_with_error))
                                    ]
    except Exception as error:
        print("Sucedió un error al enlistar los productos para traslado")
        print(error)
        return []
    if list_of_products_with_error == []:
        print("Terminado. No se encontró productos para traslado")
    else:
        print("Terminado. Productos para traslado hechos")
    return list_of_products_with_error

def change_alerted_status_of_product(list_of_products_alerted):
    """
    Esta función cambia el status de la columna "alert it?" de los productos ya alertados por Dr.Merma en
    la sheet1. Además aumenta +1 el número de "products alerted" en la celda B2 de la sheet2
    """
    rows_of_products_alerted = [(list_of_products_alerted[i][3], list_of_products_alerted[i][4]) for i in range(len(list_of_products_alerted))]

    for row_number,coordinador in rows_of_products_alerted:
        if coordinador == 'EDDY ARMESTAR':
            sheet = sheets['Mr. Mapeadores sheets'][0]
            sheet2 = sheets['Python variables sheets'][0]
        elif coordinador == 'LUIS RAMIREZ':
            sheet = sheets['Mr. Mapeadores sheets'][1]
            sheet2 = sheets['Python variables sheets'][1]
        cell = f"Z{row_number}"
        sheet.update(cell,"YES")
        contador = (int((sheet2.cell(2,2).value))) + 1
        cell = 'B2'
        sheet.update(cell,contador)
        continue

def change_alerted_status_15_days(list_of_products_traslado):
    """
    Esta función cambia el status de la columna "Error alertado" de los errores ya alertados por Dr.Errors en
    la sheet1.
    """
    rows_of_errors_alerted = [(list_of_products_traslado[i][2], list_of_products_traslado[i][3]) for i in range(len(list_of_products_traslado))]

    for row_number, coordinador in rows_of_errors_alerted:
        if coordinador == 'EDDY ARMESTAR':
            sheet = sheets['Mr. Mapeadores sheets'][0]
        elif coordinador == 'LUIS RAMIREZ':
            sheet = sheets['Mr. Mapeadores sheets'][1]
        cell = f"AA{row_number}"
        sheet.update(cell,"YES")
        continue

def run_dr_merma(list_of_products_alerted):
    """
    Función principal: Envia los productos a vencer de cada tienda a sus respectivos grupos de wsp.
    En caso no halla productos a alertar, envia un mensaje avisandolo al grupo.
    Toma como párametro la nested-list generada en "enlist_products_to_alert()"
    """
    number_products_alerted = reduce(lambda a,b: int(a)+int(b),[sheet.cell(2,2).value for sheet in sheets['Python variables sheets']])
    number_products_maped = reduce(lambda a,b: int(a)+int(b),[sheet.cell(3,2).value for sheet in sheets['Python variables sheets']]) #Sum each value of each spreadsheet
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
            if tienda[4] == '569': #La tienda 569 es un caso especial. Quieren recibir los anuncios en el RPC
                pywhatkit.sendwhatmsg('+51972795716',ms1, hour, minute+1,11)
                pywhatkit.sendwhatmsg('+51972795716',ms2, hour, minute+2,11)
                continue
            pywhatkit.sendwhatmsg_to_group(tienda[1],ms1, hour, minute+1,11)
            pywhatkit.sendwhatmsg_to_group(tienda[1],ms2, hour, minute+2,11)
        else: #Si no hay productos por vencerse, envia esto:
            ms3 = f'Felicidades. Ningún vencimiento para {tienda[0]} el día {(datetime.date.today())}\n Que la pasen bien!'
            print(minute)
            if tienda[4] == '569': #La tienda 569 es un caso especial. Quieren recibir los anuncios en el RPC
                pywhatkit.sendwhatmsg('+51972795716', ms3, hour, minute+1,11)
                continue
            pywhatkit.sendwhatmsg_to_group(tienda[1], ms3, hour, minute+1,11)

def run_dr_traslados(list_of_products_traslado):
    """
    Función principal: Envia los productos a vencer de cada tienda a sus respectivos grupos de wsp.
    En caso no halla productos a alertar, envia un mensaje avisandolo al grupo.
    Toma como párametro la nested-list generada en "enlist_products_to_alert()"
    """
    for tienda in tiendas_database: # For loop para enviar los mensajes a cada tienda
        hour = int(time.strftime("%H"))
        minute = int(time.strftime("%M")) + 1
        #Enlistar todos los nombres de productos por vencerse
        products_name = [list_of_products_traslado[i][1] for i in range(len(list_of_products_traslado)) if list_of_products_traslado[i][0] == tienda[4]]
        rows_products = [list_of_products_traslado[i][2] for i in range(len(list_of_products_traslado)) if list_of_products_traslado[i][0] == tienda[4]]
        if products_name != []: #Si hay productos con errores, envia esto:
            name_and_row_products = [(f"{products_name[i]} en la fila {rows_products[i]}") for i in range(len(rows_products))]
            products_name = "\n- ".join(name_and_row_products)
            print(products_name, "Enviando a ", tienda[0])
            ms1 = """Estos productos NO se van a vender en 15 dias: \n""" +"- "+ products_name + '\n Se recomienda coordinar traslado con otras tiendas'
            print(ms1)
            if tienda[4] == '569': #La tienda 569 es un caso especial. Quieren recibir los anuncios en el RPC
                pywhatkit.sendwhatmsg('+51972795716',ms1, hour, minute+1,18)
                continue
            pywhatkit.sendwhatmsg_to_group(tienda[1],ms1, hour, minute+1,18)
        else: #Si no hay productos con errores, continua:
            continue

def avisar_admins_consolidado():
    """
    Función para avisar a las admins de cada tienda que mapeen vencimientos del siguiente mes
    Se ejecuta si el número del día es 28.
    """
    for tienda in tiendas_database:
        hour = int(time.strftime("%H"))
        minute = int(time.strftime("%M")) + 1
        pywhatkit.sendwhatmsg(tienda[2], f"""Hola {tienda[3]}. Soy Dr.Merma. Hoy es 28, se recomienda empezar el mapeo de vencimientos del siguiente mes""", hour, minute+1)

def avisadora():
    """
    Función para avisar a los admins de los avances semanales del proyecto. Se ejecuta todos los lunes.
    """
    def mensaje(name):
        mensaje = f"""Hola {name}. Soy señorita anunciadora. Avances del frente:
        ¿Nunca tuviste un quiebre de arena de gato? Sí, es así, entonces sabes de lo que hablo.
        Imagina todas las arenas de gato que pudiste vender si hubieras tenido el stock.
        Por el momento las tiendas 569, 831 y 762 tienen su cubicaje de quiebres hecho. Este es: https://docs.google.com/spreadsheets/d/1J7ou_Z0qi2ZtiWZbRKLNUDavPA1FCUy9Hcl2sRjR-ZQ/edit#gid=204216952
        Ahora esta semana se está trabajando en solucionar el problema de los vencimientos.
        Imagina un mundo con 0 merma de vencimientos. ¿Utópico? ¿Posible? Lo descubriremos.
        Recordar que todo este trabajo se logra gracias a tu apoyo. Cualquier puedes comunicarla a Augusto. Que tengas un buen día. ;D
        Señorita anunciadora fuera.
        """
        return mensaje

    # Enviarlo a cada admin de cada tienda
    for tienda in tiendas_database:
        hour = int(time.strftime("%H"))
        if int(time.strftime("%S")) >= 51:
            minute = int(time.strftime("%M")) + 1
        else:
            minute = int(time.strftime("%M"))
        name = tienda[3]
        mensajito = mensaje(name)
        pywhatkit.sendwhatmsg(tienda[2], mensajito, hour, minute+1)
    # Enviarlo al coordinador Luis
    mensajito = mensaje('Luis')
    pywhatkit.sendwhatmsg('+51989248667', mensajito, hour, minute+6)

def run():
    # Alertar sobre los productos proximos a vencer
    print("Enlistando productos para alertar")
    list_exp_products = enlist_products_to_alert()
    if list_exp_products != []:
        print("Productos por vencerse encontrados, avisandolos")
        run_dr_merma(list_exp_products)
        print("Mensajes enviados")
    change_alerted_status_of_product(list_exp_products)
    print("Productos status cambiados")

    # Alertar sobre los productos proximos a vencer
    print("Revisando si hay productos que se deberían trasladar")
    list_products_tras = enlist_15_days_products()
    if list_products_tras != []:
        print("Productos para traslado encontrados, avisandolos")
        run_dr_traslados(list_products_tras)
        print("Traslados enviados")
        change_alerted_status_15_days(list_products_tras)
        print("Traslados status cambiados")

    # Parte del programa que envía mensajes a los admins para:
    # 1) Recordarles de hacer su consolidado.
    # 2) Avisarles de los nuevos avances con el programa.
    todays_number = int(time.strftime("%d"))
    name_of_today = time.strftime("%A")
    if todays_number == 28:
        print('Avisando a admins y coordis para mapear los proximos a vencer')
        avisar_admins_consolidado()
    if name_of_today == 'Monday':
        print("Avisando a los admin avances del frente")
        avisadora()

if __name__ == '__main__':
    print("Dr Merma iniciado")
    start = time.process_time()
    run()
    print("Dr Merma terminado. Tiempo tomado:",time.process_time() - start)
    print("""
----------------------------------------------------------""")  
# User-histories:
# - How to map a new-brand product? How do we obtain the data? Listado de stock?