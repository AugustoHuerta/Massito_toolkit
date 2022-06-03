#!/usr/bin/env python
# coding: utf-8
""" Mr. Mapeador 2.0.py

El próposito de este programa es:
    1) Parsear los xlsx de movimientos de inventario del último mes a 1 DataFrame:
        - Esto para calcular la VTM (Venta media) de cada producto en cada local Mass.

    2) Subir los DataFrames resultantes a una google spreadsheet en particular:
        - Para que la AppSheet Mr. Mapeador funcione.
        - Y, ya que cada tienda tiene un coordinador asignado, subir los datos a la hoja correspondiente
        a cada coordi.

Notas:
    - Método para obtener DFs de excels: Convertirlos a .csv primero y leerlos desde allí
    - Saca los cálculos desde el último mes.
        - Ver como optimizar este proceso para el siguiente consolidado.

User histories (Scrum):
    - 

"""

import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import numpy as np
import time
import xlrd
import csv
import os

def transform_df(df_given):
    df_new =df_given.groupby('Código de Producto',
                            as_index=False).agg({'Nombre de Prd.':lambda x: x.iloc[0],
                                                'Cantidad':'sum',  
                                                'Costo Unitario':'max',
                                                'Local':lambda x: x.iloc[0],
                                                'Descripción Area':lambda x: x.iloc[0],
                                                'Descripción Sección':lambda x: x.iloc[0],
                                                'Descripción Línea ':lambda x: x.iloc[0],
                                                'Descricpión Familia':lambda x: x.iloc[0],
                                                'Descripción Subfamilia':lambda x: x.iloc[0],
                                                'Código Proveedor':lambda x: x.iloc[0],
                                                'Nombre Proveedor':lambda x: x.iloc[0]
                                                })
    # Rounding 'Costo Unitario'
    df_new['Costo Unitario'] = round(df_new['Costo Unitario'],2)

    # Getting de VMD
    df_new['VMD'] = round(df_new['Cantidad'] / -30,2) # -90 to get average of 3 months, -30 for one.
    df_new = df_new.drop("Cantidad",axis=1)

    # Creating and ordering de 'Unique id' column
    df_new['Unique id'] = df_new['Nombre de Prd.'] +" "+ df_new['Local'].astype(str)
    df_new['Unique id'] = df_new['Unique id'].str[:-2] # Al parecer formatean el número con .0 al final
    df_new.insert(0,'Unique id',df_new.pop('Unique id')) # Move "Unique id" col to first position

    return df_new

def df_v_all_locals(dfs_given):
    lister_dfs = [] #List of all dfs we will build for each local
    for df in dfs_given:
        num_locals = df['Local'].unique() # Get np.array of all nums of all locals
        condition_just_vt = df['Cod Mov. Maestro'] == 'VT' # Condition to only get VT mvs
        df = df[condition_just_vt] # Apply condition
        for local in num_locals:
            condition_num_local = df['Local'] == local # Condition to only get VT mvs of this local
            df_local = df[condition_num_local] # Apply condition
            df_local = transform_df(df_local) # Just get the pieces of information valuable
            lister_dfs = lister_dfs + [df_local] # Add this new df to the list
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

def get_worksheet(spread_sheets):
    """
    Función para obtener la spreadsheet a la cual se le cargara el dataframe de
    la función df_v_all_locals
    """
    print("¿Cuál spreadsheet deseas usar?")
    list_sph = [sph for sph in spread_sheets.keys()]
    for i, sph in enumerate(list_sph,1):
            print(f"{i}. {sph}")
    sph_selected = list_sph[int(input("Escribe su número aquí: "))-1]
    print(f"Spreadsheet selected: {sph_selected}")
    sph_selected = spread_sheets[sph_selected]
    worksheet = sph_selected.worksheet('GM')
    return worksheet

def run():
    print("Conectandose con google sheets")
    start = time.process_time()
    scope = ["https://spreadsheets.google.com/feeds",'https://www.googleapis.com/auth/spreadsheets',"https://www.googleapis.com/auth/drive.file","https://www.googleapis.com/auth/drive"]

    creds = ServiceAccountCredentials.from_json_keyfile_name("creds.json", scope)

    client = gspread.authorize(creds)

    spread_sheets  = {
        'Mr.Mapeador LUIS': client.open('Mr.Mapeador LUIS'),
        'Mr.Mapeador EDDY': client.open('Mr.Mapeador EDDY')
    }

    print("Obteniendo worksheet")
    worksheet = get_worksheet(spread_sheets)

    # Get paths of all excels wanted to parse
    print("Obteniendo paths de los excels")

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
    if path_excel_files != []:
        for excel_file in path_excel_files:
            start2 = time.process_time()

            print("Obteniendo DF de excel", excel_file)
            path_csv = csv_from_excel(excel_file)
            df_mov = pd.read_csv(path_csv) #Toma 1 seg

            print("Anexando DF a los demás")
            dfs_mov = dfs_mov + [df_mov]

            print("Logrado. Tiempo tomado:",time.process_time() - start2)
    
    # Merge and parse all DataFrames to the final DataFrame.
    print("Transformando dataframe")
    final_df = df_v_all_locals(dfs_mov)
    
    # Uploading to google sheets
    print("Cargandolo al google sheet")
    worksheet.clear()
    worksheet.update([final_df.columns.values.tolist()] + final_df.values.tolist())
    print("Logrado. Tiempo tomado:",time.process_time() - start)
    
run()
#abril.xlsx
# Convert csv to a tiny dataframe 
#final_df.to_csv('abril2.csv', index=False) Si lo quisieramos exportar a un csv

