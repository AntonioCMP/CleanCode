

import os
import time
import datetime as dt
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
import pandas as pd
from numpy import array,zeros


PAGE= "https://www.bolsadequito.com/uploads/estadisticas/boletines/informacion-continua/maximos-y-minimos.xls"

download_dir = "D:\\DocumentosI\\NGE\\NGE3.0+1.0\\The grid\\Data"
NEW_ONE= "https://www.bolsadequito.com/index.php/mercados-bursatiles/mercado-en-linea/operaciones-cerradas"
new_name= "operaciones-cerradas" + str(dt.date.today()) + ".csv"

chrome_options = Options()
prefs = {
    "download.default_directory": download_dir, 
    "download.prompt_for_download": False,       
    "download.directory_upgrade": True,         
    "safebrowsing.enabled": True  }
              
options= webdriver.ChromeOptions()
options.add_experimental_option('excludeSwitches', ['enable-logging'])
options.add_experimental_option("detach",True)
options.add_experimental_option("prefs", prefs)

driver= webdriver.Chrome(options=options)
time.sleep(5)
driver.get(url=NEW_ONE)
time.sleep(7)
iframe = driver.find_element(By.TAG_NAME, "iframe")
driver.switch_to.frame(iframe)
element= driver.find_element(by=By.ID,value='tb2')
element.click()
archive= driver.find_element(by=By.XPATH,value='//*[@id="tblOCRV_wrapper"]/div[1]/button[3]') 
archive.click()
ruta_original = os.path.join(download_dir, "csv.csv")
time.sleep(5)

file= open(ruta_original,mode="r")
if len(file.read().split(",")) < 10:
    print("Nah, is empty")
    file.close()
    os.remove(ruta_original)

else:
    file.close()
    ruta_nueva = os.path.join(download_dir,new_name)
    time.sleep(5)
    os.rename(ruta_original, ruta_nueva)

driver.quit()


business= array(['BANCO GUAYAQUIL S.A.', 'MUTUALISTA PICHINCHA',
       'CERVECERIA NACIONAL CN S A', 'CORPORACION FAVORITA C.A.',
       'BANCO DE LA PRODUCCION S.A . PRODUBANCO', 'BANCO PICHINCHA C.A.',
       'HOLCIM ECUADOR S.A.', 'SIEMPREVERDE SA', 'TECATEAK SA',
       'CONCLINA C A  CIA CONJU CLINICO NACIONAL', 'RETRATOREC S.A.',
       'BANCO BOLIVARIANO C.A.', 'TECAFORTUNA SA',
       'BOLSA DE VALORES DE GUAYAQUIL', 'SAN CARLOS SOC. AGR. IND.',
       'CRIDESA', 'INDUSTRIAS ALES', 'BOLSA DE VALORES DE QUITO',
       'HOLDING TONICORP S.A.', 'BEVERAGE BRAND PATENTS SA',
       'LA SABANA FORESTAL (PLAINFOREST) S.A.', 'VALLE GRANDE FORESTAL',
       'LA CUMBRE FORESTAL PEAKFOREST SA', 'INVERSANCARLOS',
       'BRIKAPITAL SA', 'MULTI-BG S.A. CORPORACION', 'HOTEL COLON',
       'CERRO ALTO HIGHFOREST S A', 'MERIZA', 'EL TECAL',
       'LA VANGUARDIA FORESTAL', 'NATLUK SA',
       'CONTINENTAL TIRE ANDINA S A',
       'CIALCO CONSTRUCTORA IMPORTADORA ALVAREZ',
       'LA CAMPINA FORESTAL STRONGFOREST S A', 'CEPSA',
       'BANCO SOLIDARIO S.A.', 'BANCO AMAZONAS', 'SUPERDEPORTE S.A.',
       'BANCO DE MACHALA S.A.', 'BANCO DEL AUSTRO',
       'CERRO VERDE FORESTAL S A BIGFOREST',
       'RIO GRANDE FORESTAL RIVERFOREST SA',
       'LA ENSENADA FORESTAL COVEFORESTS SA', 'RIO CONGO FORESTAL',
       'LA COLINA FORESTAL (HILLFOREST) S.A.',
       'LA ESTANCIA FORESTAL FORESTEAD S A', 'VERDETEKA','ALICOSTA BK HOLDING S A', 'EDUCACION Y FUTURO TEKAFUTURO SA'])

#Ask for the current date and initialize different list that will help us in the processing process
day_today= str(dt.datetime.today())[:10]
today= dt.date.today()
print(day_today)
today= dt.date.today()
daily_names= ['PRODUBANCO S.A.','INVERSANCARLOS S.A. USD 1,00', 'CORPORACION  FAVORITA C.A', 'BANCO DE GUAYAQUIL USD 1', 'SOC.AG.IND.SAN CARLOS US D  1', 'CONCLINA C.A. ORDINARIA D  1', 'BANCO PICHINCHA CA D 100.00', 'BOLSA DE VALORES DE QUITO', 'PRODUBANCO S.A.', 'CERVECERIA NACIONAL CN S.A.', 'HOLCIM ECUADOR S.A.D 3', 'BEVERAGE BRAND &PATENTS COMP B', 'FONDO INV COTIZADO FIDUCIA', 'BANCO BOLIVARIANO USD 1,00', 'BOLSA DE VALORES DE GUAYAQUIL', 'ASOCIACION MUT.PICHINCHA']
level = {}



#Cleans all the extra words in the arrays
def limpiar(nombre):
    irrelevantes = {"S.A.", "USD", "C.A.", "ltda", "S.A", "US","D","1","A","S","DE","S","A","SA"}
    return set([word for word in nombre.split() if word not in irrelevantes])

#Read the current csv file with the names

daily= pd.read_csv(f"D:\\DocumentosI\\NGE\\NGE3.0+1.0\\The grid\\Data\\operaciones-cerradas{day_today}.csv")
    #Verify if there is a new name that is not in the main list
for j in daily["Emisor"].unique():
    if j in daily_names:
        print("Usual")
        continue
    else:
        daily_names.append(j)
        print("New name")


    #Create two list cleaned
new_split = [limpiar(i) for i in daily_names]
old_split = [limpiar(i) for i in business]


for i, old in enumerate(old_split):
    for j, new in enumerate(new_split):
        interseccion = old & new
        if len(old) <= 3 and len(old) > 1:
            if len(interseccion) >= 2:
                level[daily_names[j]] = business[i]
        else:
            if len(interseccion) >= 3:
                level[daily_names[j]] = business[i]

level['PRODUBANCO S.A.'] = 'BANCO DE LA PRODUCCION S.A . PRODUBANCO'
level["SOC.AG.IND.SAN CARLOS US D  1"] = 'SAN CARLOS SOC. AGR. IND.'
level["CONCLINA PREFERIDA 2500 SERIEA"] = 'CONCLINA C A  CIA CONJU CLINICO NACIONAL'
level["FONDO INV COTIZADO FIDUCIA"]= "FONDO INV COTIZADO FIDUCIA"
level["CONCLINA PREFERIDASD  1SERIEB"] = 'CONCLINA C A  CIA CONJU CLINICO NACIONAL'
level['CONCLINA C.A. ORDINARIA D  1']= 'CONCLINA C A  CIA CONJU CLINICO NACIONAL'
level['INVERSANCARLOS S.A. USD 1,00']= 'INVERSANCARLOS'
level['ASOCIACION MUT.PICHINCHA']= 'MUTUALISTA PICHINCHA'
level['FID HOTEL CIUDAD DEL RIO'] = 'FID HOTEL CIUDAD DEL RIO'
level['FONDO INV COLEC B RAICES UIO 2']= 'FONDO INV COLEC B RAICES UIO'
level['BRIKAPITAL S.A'] = 'BRIKAPITAL SA'
level['CORPETROLSA S.A'] = 'CORPETROLSA S.A'

for i in daily["Emisor"].unique():
    try:
        daily.replace({i:level[i]},inplace=True) 
    except:
        continue

array(today.strftime("%Y-%m-%d")*range(len(daily)))
dates= [f"{today.strftime("%Y-%m-%d")}" for i in range(len(daily))]
daily.insert(0,"FECHA",dates)
daily.drop(columns=["Casa Compradora","Hora Cierre"],inplace=True)
daily.columns = ['FECHA', 'EMISOR', 'VALOR','NUMERO ACCIONES', 'VALOR EFECTIVO','PRECIO', 'VALOR NOMINAL' , 'PROCEDENCIA']
daily= daily.reindex(columns=['FECHA', 'EMISOR', 'VALOR', 'VALOR NOMINAL', 'PRECIO','NUMERO ACCIONES', 'VALOR EFECTIVO', 'PROCEDENCIA'])
daily.insert(0,"Unnamed: 0",zeros(len(daily)))
with open('D:\\DocumentosI\\NGE\\NGE3.0+1.0\\The grid\\Data\\AccionesFinal.csv', 'a',newline="") as f:
    daily.to_csv(f,mode="a",index=False,header=False)