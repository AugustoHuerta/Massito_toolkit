# I know is fucking unredable yet but it works for now.
# This code use recursion in order to allow users to fix their mistakes.
# Did you get confused in a step? Just write vol + (number of mistake's step)

from ast import If
import os
import sys
from unicodedata import name
import json
from all_list import all_list

First_list = ("ENFRIADOS", "YOGURT", "CONGELADOS", "LECHES",
            "PIQUEOS Y SECOS", "PANES/PANETONES/KEKES", "CONDIMIENTOS/ADERESOS",
            "ESPECIAS","INSTANTANEAS/CONSERVAS/A.ESPECIALES"," REPOSTERIA",
            " DESAYUNOS"," GALLETAS/GOLOSINAS"," ABARROTES BASICOS",
            " GASEOSAS"," AGUAS Y FUNCIONALES"," JUGOS",
            " BEBIDAS ALCOHOL"," INCOMESTIBLES")

def list_printer(number_given): #O(1)
        contador = 1
        selected_list = all_list[number_given-1]
        for value in selected_list:
            print(''.join(['{:4}'.format(str(contador))])+ value[6])
            contador += 1
        return number_given

def storer_prod_chars(proct_wanted,quantity_expiration_date):
    division_product = proct_wanted[0]
    descripcion_area = proct_wanted[1]
    descripcion_seccion = proct_wanted[2]
    descripcion_linea = proct_wanted[3]
    descripcion_familia = proct_wanted[4]
    codigo_sku = proct_wanted[5]
    name_product = proct_wanted[6]
    cod_proveedor = proct_wanted[7]
    descrip_proveedor = proct_wanted[8]
    maped = 'NO'
    quantity = quantity_expiration_date[0]
    expiration_date = quantity_expiration_date[1]
    products_characters = [
        division_product,descripcion_area,descripcion_seccion
        ,descripcion_linea,descripcion_familia,codigo_sku
        ,name_product,cod_proveedor,descrip_proveedor
        ,quantity,expiration_date,"","","",maped,"","NO"
    ]
    return products_characters

def gets_product(proct_wanted): #O(n)
        list_products_maped = []
        # STEP 2: How many times you wanna add the product
        number_entrys_requested = str(input("PASO 2: Tipea cuantas veces vas anadirlo (Ejemplo: 3): "))
        if number_entrys_requested == 'vol1':
            os.execl(sys.executable, sys.executable, *sys.argv)
        else:
        # Asks for quantity and date of the product
            number_entrys_requested = int(number_entrys_requested)
            def get_quantity_exp(proct_wanted):
                restart_loop = 0
                quantity = (input("PASO 3: Tipea el numero de productos con esta fecha (Ejemplo: 5): "))
                if quantity == 'vol2':
                    quantity_expiration_date = gets_product(proct_wanted)
                    return quantity_expiration_date
                elif quantity == 'vol1':
                    # Restart program
                    os.execl(sys.executable, sys.executable, *sys.argv)
                while restart_loop == 0:
                    day = ((input("PASO 4: Tipea el numero del DIA de vencimiento (Ejemplo: 02): ")))
                    if day == 'vol3':
                        list_products_maped = get_quantity_exp(proct_wanted)
                        return list_products_maped
                    elif day == 'vol2':
                        quantity_expiration_date = gets_product(proct_wanted)
                        return quantity_expiration_date
                    elif day == 'vol1':
                        # Restart program
                        os.execl(sys.executable, sys.executable, *sys.argv)
                    while day is str:
                        # Checking
                        print("Solo se admiten numeros o comandos como vol + numero de paso (vol1)")
                        day = ((input("PASO 4: Tipea el numero del DIA de vencimiento (Ejemplo: 02): ")))
                    month = ((input("PASO 5: Tipea el numero del MES de vencimiento (Ejemplo: 07): ")))
                    if month == 'vol4':
                        continue
                    elif month == 'vol3':
                        list_products_maped = get_quantity_exp(proct_wanted)
                        return list_products_maped
                    elif month == 'vol2':
                        quantity_expiration_date = gets_product(proct_wanted)
                        return quantity_expiration_date
                    elif month == 'vol1':
                        os.execl(sys.executable, sys.executable, *sys.argv)
                    restart_loop = 1
                expiration_date = day + '/' + month
                quantity = int(quantity)
                quantity_expiration_date = [quantity] + [expiration_date]
                return quantity_expiration_date
            contador_entrys = 1
            while number_entrys_requested != 0:
                # name_product = proct_wanted[6]
                print(proct_wanted[6] + '. ENTRADA N*' + str(contador_entrys))
                # STEP 3, 4, 5: Insert quantity and expiration date
                quantity_exp = get_quantity_exp(proct_wanted)
                # Since there are sub-functions that can recall their mother function (E.g gets_product, get_quantity...)
                # quantity_expiration_date can have 2 cases.
                # Case 1: Have quantity and date (Everything as normal)
                # Case 2: Have a list of a all characters of a product ("get_quantity..." have recalled gets_product inside)
                # Case 1: The first value of "quantity_exp" should be an int.
                # Case 2: It should be a list.
                if type(quantity_exp[0]) is int:
                    product_stored = storer_prod_chars(proct_wanted,quantity_exp)
                    list_products_maped.append(product_stored)
                    contador_entrys += 1
                    number_entrys_requested -= 1
                    continue
                else:
                    list_products_maped = quantity_exp
                    break
        return list_products_maped

def run():
    # STEP 1: What product you wanna add?
    print("Listado de tipos de productos")
    contador = 1
    for value in First_list: #O(1)
        print(''.join(['{:2}'.format(str(contador))])+ value)
        contador += 1
    kind_of_proct_wanted = int(input("Escribe el numero del tipo producto deseado: "))

    list_products_maped = []
    wanna_continue = 'Y'
    while wanna_continue == 'Y': #O(n)
        # PASO 2: Select the product wanted
        print("Listado de productos")
        selected_list = all_list[list_printer(kind_of_proct_wanted)-1]
        number_of_proct_wanted = int(input(""""Escribe el numero del producto deseado: """))
        # Searchs the product wanted by the number selected
        proct_wanted = selected_list[(number_of_proct_wanted-1)]
        print("Producto selected: " + proct_wanted[6])
        list_products_maped.append(gets_product(proct_wanted))
        print(list_products_maped)
        wanna_continue = input("¿Quieres anadir otro producto de la misma lista? (Y/N)")
    #inserts_product_database(list_products_maped)

if __name__ == '__main__':
    run()