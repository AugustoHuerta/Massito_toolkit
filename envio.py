class envio():
    """
    Envio es una clase que contiene lo que se va a enviar a la google sheet. 
    Se considera un "envio" a todas las entradas con fechas 
    y cantidades diferentes de un producto al google sheet.
    """
    def __init__(self, product, list_d_a_q):
        """
        1. product: should be a tuple of "all_list.py" containing all product's metadata
        (Division, descripción sección, código proveedor, etc).
        2. list_d_a_q (Date and quantity): should be a list containing lists of the date and quantity of products entrance.
        Example:
        lista_chars = [
                        [45, 12/04],
                        [56, 13/05]
                        ]
        3. envio: Is the nested list contanining all the metadata required to be updated of each entry.
        each of this metadata (Product's properties) is paired with a specific column of the google sheet.
        (See the comments next to each one)
        """
        self.envio = [
                       [product[0], # division_product
                        product[1], # descripcion_area
                        product[2], # descripcion_seccion
                        product[3], # descripcion_linea
                        product[4], # descripcion_familia
                        product[5], # codigo_sku
                        product[6], # name_product
                        product[7], # cod_proveedor
                        product[8], # descrip_proveedor
                        list_d_a_q[i][0], # quantity
                        list_d_a_q[i][1], # expiration_date
                        "",
                        "",
                        "",
                        "",
                        'NO' # maped
                        ]
                    for i in range(len(list_d_a_q))
                    ]

    def enviarse(self):
        """
        Como su nombre dice, envia todas las entrys (nested lists) del atributo "envio" a la google sheet.
        """
        import gspread
        from oauth2client.service_account import ServiceAccountCredentials

        scope = ["https://spreadsheets.google.com/feeds",'https://www.googleapis.com/auth/spreadsheets',"https://www.googleapis.com/auth/drive.file","https://www.googleapis.com/auth/drive"]

        creds = ServiceAccountCredentials.from_json_keyfile_name("creds.json", scope)

        client = gspread.authorize(creds)

        spread_sheet = client.open("Massito") # Open the spreadhseet

        sheet1 = spread_sheet.worksheet('Mr.Mapeador database')

        sheet2 = spread_sheet.worksheet('Python variables')

        for i in range(len(self.envio)): #O(n)
            entry_to_be_inserted = self.envio[i]
            sheet1.insert_row(entry_to_be_inserted,3)  # Insert the list as a row at index 3
            cell = 'B3'
            contador = (int((sheet2.cell(3,2).value))) + 1
            sheet2.update(cell,contador)
            print(f"Envio de entrada {i+1} del producto {self.envio[i][0]} hecho.")