
import os
import time
import datetime as dt
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options

def scraping():
    PAGE= "https://www.bolsadequito.com/uploads/estadisticas/boletines/informacion-continua/maximos-y-minimos.xls"

    download_dir = "D:\\DocumentosI\\NGE\\NGE3.0+1.0\\The grid\\Data"
    NEW_ONE= "https://www.bolsadequito.com/index.php/mercados-bursatiles/mercado-en-linea/operaciones-cerradas"
    new_name= "operaciones-cerradas" + str(dt.date.today()) + ".csv"

    chrome_options = Options()
    prefs = {
        "download.default_directory": download_dir, 
        "download.prompt_for_download": False,       
        "download.directory_upgrade": True,         
        "safebrowsing.enabled": True                
    }

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
scraping()
