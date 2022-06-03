#!/usr/bin/env python
# coding: utf-8

""" Uploader.py

El próposito de este programa es:
    1) Subir a google sheets el cubícaje de 'Agente doble 0'.
        - 'Agente doble 0' crea un archivo "cubiculos.csv" de su análisis.
        -  Lo leemos como DataFrame con el método 'read_csv' de pandas.
        -  Subimos este DataFrame a la google sheet 'Nuevo cubicaje' del spreadhsheet 'Mr.Mapeador LUIS'

Notas:
    - 
    
User histories (Scrum):
    - 

"""

import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import numpy as np
import time

def get_worksheet(spread_sheets):
    """
    Función para obtener la spreadsheet a la cual se le cargara el dataframe de
    la función df_v_all_locals
    """
    print("¿Cuál spreadsheet deseas usar?")
    list_sph = [sph for sph in spread_sheets.keys()]
    for i, sph in enumerate(list_sph,1):
            print(f"{i}. {sph}")
    #sph_selected = list_sph[int(input("Escribe su número aquí: "))-1]
    sph_selected = list_sph[0] #Que por defecto sea 'Luis para agilizar las cosas
    print(f"Spreadsheet selected: {sph_selected}")
    sph_selected = spread_sheets[sph_selected]
    
    worksheet = sph_selected.worksheet('Nuevo cubicaje')
    return worksheet

def run():
    print("Conectandose con google sheets")
    start = time.process_time()
    scope = ["https://spreadsheets.google.com/feeds",'https://www.googleapis.com/auth/spreadsheets',"https://www.googleapis.com/auth/drive.file","https://www.googleapis.com/auth/drive"]

    creds = ServiceAccountCredentials.from_json_keyfile_name("creds.json", scope)

    client = gspread.authorize(creds)

    spread_sheets  = {
        'Mr.Mapeador LUIS': client.open('Mr.Mapeador LUIS'),
    }

    print("Obteniendo worksheet")
    worksheet = get_worksheet(spread_sheets)
    
    print("Transformando dataframe")
    final_df = pd.read_csv("cubiculos.csv")
    
    print("Cargandolo al google sheet")
    worksheet.clear()
    worksheet.update([final_df.columns.values.tolist()] + final_df.values.tolist())
    print("Logrado. Tiempo tomado:",time.process_time() - start)
    
if __name__ == '__main__':
    run()
#abril.xlsx
# Convert csv to a tiny dataframe 
#final_df.to_csv('abril2.csv', index=False) Si lo quisieramos exportar a un csv

