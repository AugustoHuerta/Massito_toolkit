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

def df_v_all(dfs_given):
    lister_dfs = [] #List of all dfs we will build for each local
    for i,df in enumerate(dfs_given):
        filtered_columns = ['Código de Producto', 'Nombre de Prd.', 'Unidad', 'Cantidad',
                           'Costo Unitario', 'Balance de inventario', 'Local',
                           'Fecha Movimiento','Descripción Mov. Maestro','Descripción Sección',
			            'Descripción Línea', 'Descricpión Familia', 'Descripción Subfamilia']
        df = df.reindex(columns = filtered_columns)

        df['Fecha Movimiento'] = df['Fecha Movimiento'].astype('string')
        df['Descripción Línea'] = df['Descripción Línea'].astype('string')
        df['Fecha Movimiento'] = pd.to_datetime(df['Fecha Movimiento']).dt.strftime('%d/%m/%Y')
        
        #c_mv_es = lambda movimiento: df['Descripción Mov. Maestro'] == movimiento
        #df = df[c_mv_es('Ventas')]

        df["N. de Df"] = i
        lister_dfs = lister_dfs + [df] # Add this new df to the list
    final_df = pd.concat(lister_dfs,ignore_index=True) # Concat all dfs of the list
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
    print("¿Qué exceles deseas subir?")
    for i, f in enumerate(excel_files,1):
            print(f"{i}. {f}")
    file_selected = excel_files[int(input("Escribe su número aquí: "))-1]
    print(f"File selected: {file_selected}")
    return file_selected

def run():
    
    # Get paths of all excels wanted to parse
    print("Iniciando programa")

    path_excel_files = []
    while True:
        print("Obteniendo archivo")
        path_excel_files.append(get_excel_file())

        wanna_more_excels =  input("¿Quieres añadir otro excel? N/Y: ")

        if wanna_more_excels.capitalize() == 'N':
            break
    
    # Converting all of these excels to pandas DataFrames
    print("Leyendo DataFrames original")

    dfs_mov = []
    ### Runs the csv_from_excel function:
    #path_csv = csv_from_excel(excel_file) # Toma 29 segundos
    #df_mov = pd.read_csv(path_csv) #Toma 1 seg
    if path_excel_files != []:
        for excel_file in path_excel_files:
            start2 = time.process_time()

            print("Obteniendo DF de excel", excel_file)
            df_mov = pd.read_excel(excel_file) #Toma cerca de 31 seg

            print("Anexando DF a los demás")
            dfs_mov = dfs_mov + [df_mov]

            print("Logrado. Tiempo tomado:",time.process_time() - start2)


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