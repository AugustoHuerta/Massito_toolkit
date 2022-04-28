def inserts_product_database(list_products_maped):
    import gspread
    from oauth2client.service_account import ServiceAccountCredentials
        
    scope = ["https://spreadsheets.google.com/feeds",'https://www.googleapis.com/auth/spreadsheets',"https://www.googleapis.com/auth/drive.file","https://www.googleapis.com/auth/drive"]

    creds = ServiceAccountCredentials.from_json_keyfile_name("creds.json", scope)

    client = gspread.authorize(creds)

    spread_sheet = client.open("Massito") # Open the spreadhseet

    sheet1 = spread_sheet.worksheet('Mr.Mapeador database')

    sheet2 = spread_sheet.worksheet('Python variables')

    sheet3 = spread_sheet.worksheet('DataJst')

    # Inserts the product in the database
    for index in tuple(range(0,len(list_products_maped))): #O(n)
        product_to_be_inserted = list_products_maped[index]
        sheet1.insert_row(product_to_be_inserted,3)  # Insert the list as a row at index 2
        cell = 'B3'
        contador = (int((sheet2.cell(3,2).value))) + 1
        sheet2.update(cell,contador)
    print("Hecho")