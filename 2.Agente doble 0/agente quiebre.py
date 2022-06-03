import pandas as pd
import numpy as np
from functools import reduce
import time
import xlrd
import converter
import Uploader

def get_values_weeks(product, local, pivot_tabler):
    """
    Expects code of product (int) and which local (int) we are talking about.
    Returns a numpy array.
    """ 
    sales_per_week = np.array([pivot_tabler.loc[product,[local]].iloc[:,i] for i in range(4)])
    possible_values = reduce(lambda a,b: a*b, sales_per_week.shape)
    sales_per_week = sales_per_week.reshape((possible_values))
    return sales_per_week

def new_cubicaje(sales_per_week):
    """
    sales_per_week is a unsorted numpy array.
    """
    sales_per_week.sort()
    q1, q3 = np.percentile(sales_per_week,75) , np.percentile(sales_per_week,25)
    iqr = (q1 - q3)
    lower_bound, upper_bound  = (q1-(1.5*iqr)), (q3+(2.0*iqr)) #2.5 porque puede pasa que hay picos
    no_outliers = []
    outliers_quiebre = False
    for x in sales_per_week:
        if (x < lower_bound):
            outliers_quiebre = True
            continue
        elif (x > upper_bound):
            continue
        else:
            no_outliers.append(x)
    no_outliers = np.array(no_outliers)
    bad_mean, good_mean = round(np.mean(sales_per_week)) * 4, round(np.mean(no_outliers)) * 4
    # Bad mean also equals to VTM
    if outliers_quiebre == True:
        if good_mean > bad_mean:
            return (good_mean, bad_mean)
        return False
    else:
        return False

def all_cubicajes(df):
    c_mv_es = lambda movimiento: df['Descripción Mov. Maestro'] == movimiento
    df = df[c_mv_es('Ventas')].reset_index()
    df['Descripción Línea'].fillna("Datos corruptos", inplace= True)
    
    locales = df["Local"].unique()
    list_products_sku = df['Código de Producto'].drop_duplicates()
    pivot_tabler = df.pivot_table(index=['Código de Producto', 'N. Mes'],columns=['Local','N. Semana'], values='Cantidad',aggfunc='sum')
    pivot_tabler = (pivot_tabler * -1).fillna(0) # Negativos a positivos y sacar los NaN a 0
    grupi = df.groupby('Código de Producto').agg({'Costo Unitario':'max',
                                                'Nombre de Prd.':lambda x: x.iloc[0],
                                               'Nombre de Prd.':lambda x: x.iloc[0],
                                               'Descripción Sección':lambda x: x.iloc[0],
                                               'Descripción Línea':lambda x: x.iloc[0],
                                               'Descricpión Familia':lambda x: x.iloc[0],
                                               'Descripción Subfamilia':lambda x: x.iloc[0],
                                                })
    list_arrays = []
    for local in locales:
        for product_sku in list_products_sku:
            sales_per_week = get_values_weeks(product_sku, local, pivot_tabler)
            new_cubiculo = new_cubicaje(sales_per_week)
            if new_cubiculo == False:
                continue
            cost_max = round(grupi.loc[product_sku][0])
            name_prod = grupi.loc[product_sku][1]
            seccion = grupi.loc[product_sku][2]
            linea = grupi.loc[product_sku][3]
            familia = grupi.loc[product_sku][4]
            subfamilia = grupi.loc[product_sku][5]
            sugerido_cubicaje = new_cubiculo[0]
            VTMM = new_cubiculo[1]
            VTMD = round(VTMM / 30, 2)
            unidades_perdidas = sugerido_cubicaje - VTMM
            cuanto_se_esta_perdiendo_soles = (sugerido_cubicaje - VTMM) * cost_max
            list_arrays.append(np.array([product_sku, name_prod,
                                         local, sugerido_cubicaje,
                                         VTMM, VTMD, unidades_perdidas,
                                         cuanto_se_esta_perdiendo_soles, seccion,
                                         linea, familia, subfamilia]))
    return np.concatenate([list_arrays])

def run():
    print("Obtieniendo data")
    start1 = time.process_time()
    f_df = converter.run()
    print("Logrado. Tiempo tomado:",time.process_time() - start1)

    print("Obteniendo quiebres")
    start = time.process_time()
    data_quiebres = all_cubicajes(f_df)
    print("Logrado. Tiempo tomado:",time.process_time() - start)
    
    print("Pasando quiebres y all_data a df y .csv")
    start = time.process_time()
    headers = ['Producto SKU', 'Nombre producto', 'Local', 'Sugerido cubicaje',
               'VTM (Mes)', 'VTM (Diario)', "Cuanto se pierde (UN)", "Cuanto se pierde (soles)",
               'Seccion', 'Linea', 'Familia','Subfamilia']
    cubiculos = pd.DataFrame(data_quiebres,columns=headers)
    cubiculos['Producto SKU'] = cubiculos['Producto SKU'].astype(int)

    cubiculos.to_csv("cubiculos.csv", index=False)
    f_df.to_csv("df_movimientos_inv_all_data.csv", index=False)
    print("Logrado. Tiempo tomado:",time.process_time() - start)

    Uploader.run()

    #if (input("¿Te gustaría subirlo al google sheet? Y/N").capitalize() == 'Y') or (True):
    #    Uploader.run()
    print("TODO el programa realizado en: ", time.process_time() - start1)


if __name__ == '__main__':
    run()