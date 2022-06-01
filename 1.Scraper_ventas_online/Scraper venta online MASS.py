import html5lib
import pandas as pd
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait #This and the other one waits
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import Select # Para obtener todos los valores de todas las fechas
import time
from creds_ventas import USERNAME
from creds_ventas import PASSWORD
from creds_ventas import url_base
from creds_ventas import headers

def parse_table(table_soup):
    data_for_df = []
    table_body = table_soup.find('tbody')
    rows = table_body.find_all('tr')
    for row in rows:
        cols = row.find_all('td')
        cols = [element.text.strip() for element in cols]
        data_for_df.append([element for element in cols if element]) # Get rid of empty values
    return data_for_df

start = time.process_time() # NO cuenta modulos ni funciones

options = webdriver.ChromeOptions()
options.add_argument("start-maximized")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)
driver = webdriver.Chrome(executable_path='/home/sebas/Desktop/massito/scraper/chromedriver',options=options)

# Entrar a la URL
driver.get(url_base)
# -Primera vez: Me pide usuario y contraseña.
# - Sí. Lo pide mientras no guardes contra ni usuario en el webdriver.

username = driver.find_element(By.XPATH,'//*[@id="txtLogin"]')
password = driver.find_element(By.XPATH,'//*[@id="txtPasw"]')

username.send_keys(USERNAME)
password.send_keys(PASSWORD)

driver.find_element_by_id("Button1").click()

# Por si lo usamos justo cuando se creó un nuevo día
drp_fecha = Select(driver.find_element(By.TAG_NAME, 'select'))
all_dates = [date.get_attribute('value') for date in drp_fecha.options]
drp_fecha.select_by_value(all_dates[2])

# Seleccionar SPSA
driver.find_element(By.XPATH,'//*[@id="form1"]/div[3]/table[2]/tbody/tr[2]/td[1]/a').click()

# Seleccionar MASS
driver.find_element(By.XPATH,'//*[@id="form1"]/div[3]/table[2]/tbody/tr[5]/td[1]/a').click()

lister_dfs = []
headers = headers

# Esto carga todos los datos de cada día en el listado
for date in all_dates:
    drp_fecha = Select(driver.find_element(By.TAG_NAME, 'select'))
    drp_fecha.select_by_value(date)
    print("Obteniendo datos de:", date)
    ###
    html = driver.page_source
    soup = BeautifulSoup(html,'html.parser')
    table_soup = soup.find("table", {"id":"datos"})
    data_all_sucursales = parse_table(table_soup)
    df = pd.DataFrame(data_all_sucursales, columns = headers)
    # Mala (La primera tienda de la lista) aparece como el segundo elemento aquí.
    # Loreto (La última tienda de la lista) aparece como el antepenultimo elemento aquí.
    df = df[1:-3] # Así que recortamos nuestra lista
    df['Day'] = date # Sentado día
    ###
    lister_dfs.append(df)
    print("Datos obtenidos con exito!")

driver.close()

final_df = pd.concat(lister_dfs,ignore_index=True)

final_df.to_csv('ventas_31_dias.csv', index=False)

print("LOGRADOOOO. Tiempo tomado:", time.process_time() - start)
