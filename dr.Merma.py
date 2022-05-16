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
    ['Del Aire', '', '+51935924465','Luz', '487'],
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
    print("Enlistando productos por vencer")
    try:
        minimarkets_of_products_not_alerted = [value for sheet in sheets['Python variables sheets'] for value in sheet.col_values(3)[1:]] # Getting all "Tienda" numbers of all products.
        names_of_products_not_alerted = [value for sheet in sheets['Python variables sheets'] for value in sheet.col_values(4)[1:]] # Getting all names of all products.
        daysleft_of_products_not_alerted = [value for sheet in sheets['Python variables sheets'] for value in sheet.col_values(5)[1:]] # Getting all "days left"s value of all products.
        rownumber_of_products_not_alerted = [value for sheet in sheets['Python variables sheets'] for value in sheet.col_values(6)[1:]] # Getting all row numbers of all products.
        coordinador = [value for sheet in sheets['Python variables sheets'] for value in sheet.col_values(7)[1:]] # Getting the name of the coordinador.
        list_of_products_not_alerted = [
                                        [
                                            minimarkets_of_products_not_alerted[i], # Getting "Tienda" number of each product
                                            names_of_products_not_alerted[i], # Getting the name of each product
                                            daysleft_of_products_not_alerted[i], # Getting "the days left" value of each product
                                            rownumber_of_products_not_alerted[i], # Getting the row number of each product
                                            coordinador[i]
                                        ]
                                        for i in range(len(names_of_products_not_alerted))
                                        if ( (minimarkets_of_products_not_alerted[i] != '1162') or (int(daysleft_of_products_not_alerted[i]) < -1) )
                                        # La tienda 1162 es un caso especial debido a que hacen sus mermas por reglas de 3 días antes del vencimiento.
                                    ]
    except Exception as error:
        print("Sucedió un error al enlistar productos por vencer")
        print(error)
    if list_of_products_not_alerted == []:
        print("Terminado. No se encontró productos por vencerse")
    else:
        print("Terminado. Productos por vencerse enlistados")
        print(list_of_products_not_alerted)
    return list_of_products_not_alerted

def enlist_products_errors():
    """
    Esta función extrae todos los productos que tienen un valor unitario de 0 y retorna una nested-list
    con el nombre de este producto y en qué columnas se encuentran.
    Esto porque no tiene sentido. ¿Cómo vas a mapear un producto que, según tu inventario, no tienes?
    """
    print("Enlistando productos con errores")
    try:
        minimarkets_of_products_with_error = [value for sheet in sheets['Python variables sheets'] for value in sheet.col_values(8)[1:]] # Getting all "Tienda" numbers of all products. # Getting all "Tienda" numbers of all products.
        names_of_products_with_error = [value for sheet in sheets['Python variables sheets'] for value in sheet.col_values(9)[1:]] # Getting all names of all products.
        rownumber_of_products_with_error = [value for sheet in sheets['Python variables sheets'] for value in sheet.col_values(10)[1:]] # Getting all row numbers of all products.
        coordinador = [value for sheet in sheets['Python variables sheets'] for value in sheet.col_values(11)[1:]] # Getting the name of the coordinador.
        list_of_products_with_error = [
                                        [
                                            minimarkets_of_products_with_error[i], # Getting "Tienda" number of each product
                                            names_of_products_with_error[i], # Getting the name of each product
                                            rownumber_of_products_with_error[i], # Getting the row number of each product
                                            coordinador[i]
                                        ]
                                        for i in range(len(minimarkets_of_products_with_error))
                                    ]
    except Exception as error:
        print("Sucedió un error al enlistar los productos con errores")
        print(error)
    if list_of_products_with_error == []:
        print("Terminado. No se encontró productos con errores")
    else:
        print("Terminado. Errores enlistados con exito")
    return list_of_products_with_error

def enlist_15_days_products():
    """
    Esta función extrae todos los productos que no van a venderse en 15 dias y retorna una nested-list
    con el nombre de este producto y en qué columnas se encuentran.
    Esto para que los admins puedan hacer traslasdo de esos productos antes
    """
    print("Enlistando productos con errores")
    try:
        minimarkets_of_products_with_error = [value for sheet in sheets['Python variables sheets'] for value in sheet.col_values(15)[1:]] # Getting all "Tienda" numbers of all products. # Getting all "Tienda" numbers of all products.
        names_of_products_with_error = [value for sheet in sheets['Python variables sheets'] for value in sheet.col_values(16)[1:]] # Getting all names of all products.
        rownumber_of_products_with_error = [value for sheet in sheets['Python variables sheets'] for value in sheet.col_values(17)[1:]] # Getting all row numbers of all products.
        coordinador = [value for sheet in sheets['Python variables sheets'] for value in sheet.col_values(18)[1:]] # Getting the name of the coordinador.
        list_of_products_with_error = [
                                        [
                                            minimarkets_of_products_with_error[i], # Getting "Tienda" number of each product
                                            names_of_products_with_error[i], # Getting the name of each product
                                            rownumber_of_products_with_error[i], # Getting the row number of each product
                                            coordinador[i]
                                        ]
                                        for i in range(len(minimarkets_of_products_with_error))
                                    ]
    except Exception as error:
        print("Sucedió un error al enlistar los productos para traslado")
        print(error)
    if list_of_products_with_error == []:
        print("Terminado. No se encontró productos para traslado")
    else:
        print("Terminado. Productos para traslado hechos")
    return list_of_products_with_error

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

def change_alerted_status_error(list_of_products_errors):
    """
    Esta función cambia el status de la columna "Error alertado" de los errores ya alertados por Dr.Errors en
    la sheet1.
    """
    rows_of_errors_alerted = [(list_of_products_errors[i][2], list_of_products_errors[i][3]) for i in range(len(list_of_products_errors))]

    for row_number, coordinador in rows_of_errors_alerted:
        if coordinador == 'EDDY ARMESTAR':
            sheet = sheets['Mr. Mapeadores sheets'][0]
        elif coordinador == 'LUIS RAMIREZ':
            sheet = sheets['Mr. Mapeadores sheets'][1]
        cell = f"AC{row_number}"
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
            if tienda[4] == '487': #La tienda 487 es un caso especial. No estoy en su grupo.
                pywhatkit.sendwhatmsg(tienda[2],ms1, hour, minute+1,11)
                pywhatkit.sendwhatmsg(tienda[2],ms2, hour, minute+2,11)
                continue
            elif tienda[4] == '569': #La tienda 569 es un caso especial. Quieren recibir los anuncios en el RPC
                pywhatkit.sendwhatmsg('+51972795716',ms1, hour, minute+1,11)
                pywhatkit.sendwhatmsg('+51972795716',ms2, hour, minute+2,11)
                continue
            pywhatkit.sendwhatmsg_to_group(tienda[1],ms1, hour, minute+1,11)
            pywhatkit.sendwhatmsg_to_group(tienda[1],ms2, hour, minute+2,11)
        else: #Si no hay productos por vencerse, envia esto:
            ms3 = f'Felicidades. Ningún vencimiento para {tienda[0]} el día {(datetime.date.today())}\n Que la pasen bien!'
            print(minute)
            if tienda[4] == '487': #La tienda 487 es un caso especial. No estoy en su grupo.
                pywhatkit.sendwhatmsg(tienda[2], ms3, hour, minute+1,11)
                continue
            pywhatkit.sendwhatmsg_to_group(tienda[1], ms3, hour, minute+1,11)

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
            elif tienda[4] == '569': #La tienda 569 es un caso especial. Quieren recibir los anuncios en el RPC
                pywhatkit.sendwhatmsg('+51972795716',ms1, hour, minute+1,18)
                continue
            pywhatkit.sendwhatmsg_to_group(tienda[1],ms1, hour, minute+1,18)
        else: #Si no hay productos con errores, continua:
            continue

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
            if tienda[4] == '487': #La tienda 487 es un caso especial. No estoy en su grupo.
                pywhatkit.sendwhatmsg(tienda[2],ms1, hour, minute+1,18)
                continue
            elif tienda[4] == '569': #La tienda 569 es un caso especial. Quieren recibir los anuncios en el RPC
                pywhatkit.sendwhatmsg('+51972795716',ms1, hour, minute+1,18)
                continue
            pywhatkit.sendwhatmsg_to_group(tienda[1],ms1, hour, minute+1,18)
        else: #Si no hay productos con errores, continua:
            continue

def avisar_actualizar_data():
    """
    Función para avisar a los admins que actualizen el Listado de stock por ser viernes (Cambio de precios).
    """
    for tienda in tiendas_database:
        hour = int(time.strftime("%H"))
        minute = int(time.strftime("%M")) + 1
        pywhatkit.sendwhatmsg(tienda[2], f"""Hola {tienda[3]}. Soy Dr.Merma. Hoy es viernes, te recomiendo actualizar tu listado de stock por el cambio de precio \nLo encuentras el excel de Mr.Mapeador en "Data + Número de tienda" """, hour, minute+1)

def avisar_admins_consolidado():
    """
    Función para avisar a las admins de cada tienda que mapeen vencimientos del siguiente mes
    """
    for tienda in tiendas_database:
        hour = int(time.strftime("%H"))
        minute = int(time.strftime("%M")) + 1
        pywhatkit.sendwhatmsg(tienda[2], f"""Hola {tienda[3]}. Soy Dr.Merma. Hoy es 28, se recomienda empezar el mapeo de vencimientos del siguiente mes""", hour, minute+1)

def avisadora():
    """
    Función para avisar a los admins de los avances semanales del proyecto. Avisa si es Lunes
    """
    def mensaje(name):
        mensaje = f"""Hola {name}. Soy señorita anunciadora. Avances del frente:
        1. Mr. Mapeador ya tiene la venta promedio agregadada. Lo puedes ver en el excel ;D.
        - Además:
            a) Se ha agregado una columna incluyendo coordinador de cada tienda.
            b) Sale en rojo los productos que NO vas a poder vender en el tiempo que se van vencer.
            c) Se ha agregado codigo de proveedor y descripción de proveedor.
            d) Ahora los avisos de Dr. Merma son en base al cronograma de retiro. Esto aplica para todas las tiendas excepto Garzón 6 (Nosotros podemos bapear)
        2. Dr. Merma ya avisa 15 dias con anterioridad si tienes la capacidad de vender o no el producto.
        - Esto para que puedas hacer una gestión de emergencia y trasladarlo entre otras tiendas.
        3. Además. Gracias al apoyo de todas las tiendas y del diablo (Luzmary):
            a) Ya se tiene la base de datos necesaria para automatizar el cubicaje.
            b) Se esta ya programando el robot que envia correos automaticamente a los de ventas.
            c) Ahora se está configurando el reporte de dinero perdido por cada tienda. Esto por las ventas que pierdes por quiebre y el dinero mermado en vencimientos.

        ¿Qué se va a trabajar esta semana?
        1. Configuración e impulsación de Madam Ventas.
        - Ella se encargará de automatizar tu cubicaje lo más posible, para tu tienda y todas las demás.
        - Se calcula que ayudará a ganar 125,000 soles mensuales a todo el formato en ahorro de merma y quiebre de venta.
        2. Solución de errores.
        - Evitar que Mr. Mapeador saque como "0" productos que SÍ están en stock.
        3. Comunicación con los coordinadores Edi y Luis:
        - Esto para elevar la conversación a niveles más altos con el objetivo de la venta a tiendas Mass.

        Eso sería todo la verdad. Massito, Dr. Merma, Mr. Mapeador y yo esperamos lograrlo.
        Recuerda que puedes chequear nuestro impacto con este reporte en vivo! (En desarrollo): https://datastudio.google.com/reporting/60594fa0-98c5-47ae-a14f-6c2208be8331/page/LJWsC
        No olvides, {name} que sin tu apoyo esto no habría sido posible"""
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
    print("Empezando programa")
    list_exp_products = enlist_products_to_alert()
    if list_exp_products != []:
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
    list_products_tras = enlist_15_days_products()
    if list_products_tras != []:
        run_dr_traslados(list_products_tras)
        print("Traslados enviados")
        change_alerted_status_15_days(list_products_tras)
        print("Traslados status cambiados")
    todays_number = int(time.strftime("%d"))
    name_of_today = time.strftime("%A")
    if name_of_today == 'Friday':
        print("Avisando a los admin para actualizar el listado de stock")
        avisar_actualizar_data()
    if todays_number == 28:
        print('Avisando a admins para mapear los proximos a vencer')
        avisar_admins_consolidado()
    if name_of_today == 'Monday':
        print("Avisando a los admin avances del frente")
        avisadora()

if __name__ == '__main__':
    run()
    print("""
----------------------------------------------------------""")  
# Configurarlo para el caso de Luzuriaga