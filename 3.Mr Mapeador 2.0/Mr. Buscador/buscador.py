#!/usr/bin/env python
# coding: utf-8

""" Converter.py

El próposito de este programa es:
    1) Parsear los xlsx de movimientos de inventario del último trimestre a 1 DataFrame.
        - Para luego análizarlo en el proyecto 'Agente doble 0'.

Notas:
    - Método para obtener DFs de excels: Leerlos con 'read_excel()' pandas method.

User histories (Scrum):
    - 

"""

import json
from lib2to3.pgen2.pgen import DFAState
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import numpy as np
import time
import xlrd
import csv
import os
import datetime as datetime

def n_week_given_date(date):
    number_day = int(date.strftime("%d"))
    if number_day < 8:
        return 1
    elif (number_day >= 8) and (number_day < 15):
        return 2
    elif (number_day >= 15) and (number_day < 22):
        return 3
    elif (number_day >= 22) and (number_day <= 31):
        return 4
    else:
        return 'Something is wrong here'

def df_v_all(dfs_given):
    lister_dfs = [] #List of all dfs we will build for each local
    for df in dfs_given:
        filtered_columns = ['Código de Producto', 'Nombre de Prd.', 'Unidad', 'Cantidad',
                           'Costo Unitario', 'Balance de inventario', 'Local',
                           'Fecha Movimiento','Descripción Mov. Maestro','Descripción Sección',
			            'Descripción Línea', 'Descricpión Familia', 'Descripción Subfamilia']
        df = df.reindex(columns = filtered_columns)

        df['Fecha Movimiento'] = pd.to_datetime(df['Fecha Movimiento'])

        df["N. Semana"] = df['Fecha Movimiento'].apply(n_week_given_date)
        df["N. Mes"] = df['Fecha Movimiento'].apply(lambda date: int(date.strftime("%m")))
        df["Día"] = df['Fecha Movimiento'].apply(lambda date: date.strftime("%A"))
        
        df['Descripción Línea'] = df['Descripción Línea'].astype('string')
        
        #c_mv_es = lambda movimiento: df['Descripción Mov. Maestro'] == movimiento
        #df = df[c_mv_es('Ventas')]

        lister_dfs = lister_dfs + [df] # Add this new df to the list
    final_df = pd.concat(lister_dfs, ignore_index=True) # Concat all dfs of the list
    return final_df

def csv_from_excel(path_to_csv):
    wb = xlrd.open_workbook(path_to_csv)
    sh = wb.sheet_by_name('DataJst01')
    your_csv_file = open('new1.csv', 'w')
    wr = csv.writer(your_csv_file, quoting=csv.QUOTE_ALL)

    for rownum in range(sh.nrows):
        wr.writerow(sh.row_values(rownum))

    your_csv_file.close()

    return 'new1.csv'

def get_excel_file():
    """
    Función para obtener qué archivo es el que se desea transformar y enviar a la spreadsheet
    """
    excel_files = [f for f in os.listdir('.') if (os.path.isfile(f)) and (f.endswith(('.xlsx', '.xls')))]
    print("¿Qué excel deseas usar?")
    for i, f in enumerate(excel_files,1):
            print(f"{i}. {f}")
    file_selected = excel_files[int(input("Escribe su número aquí: "))-1]
    print(f"File selected: {file_selected}")
    return file_selected

def run():
    
    # Get paths of all excels wanted to parse
    print("Iniciando programa")

    print("Obteniendo excels de movimientos de inventario")
    excel_file = get_excel_file()

    # Converting all of these excels to pandas DataFrames
    print("Leyendo DataFrames original")

    ### Runs the csv_from_excel function:
    #path_csv = csv_from_excel(excel_file) # Toma 29 segundos
    #df_mov = pd.read_csv(path_csv) #Toma 1 seg
    start2 = time.process_time()

    print("Obteniendo DF de excel", excel_file)
    df_mov = pd.read_excel(excel_file) #Toma cerca de 31 seg

    print("Excel leído")

    print("Logrado. Tiempo tomado:",round(time.process_time() - start2, 2))

    # Merge and parse all DataFrames to the final DataFrame.
    print("Transformando dataframe")
    final_df = df_v_all(dfs_mov)
    
    # Getting the final Dataframe
    print("Finalizando")
    return final_df
    
if __name__ == '__main__':
    run()
#abril.xlsx
# Convert csv to a tiny dataframe 
#final_df.to_csv('abril2.csv', index=False) Si lo quisieramos exportar a un csv