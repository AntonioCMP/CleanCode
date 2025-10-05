
from os import path,remove,rename
from time import sleep
from datetime import date
from selenium.webdriver import ChromeOptions,Chrome
from selenium.webdriver.common.by import By

def scraping():


    download_dir = "Data"
    NEW_ONE= "https://www.bolsadequito.com/index.php/mercados-bursatiles/mercado-en-linea/operaciones-cerradas"
    new_name= "operaciones-cerradas" + str(date.today()) + ".csv"

    prefs = {
        "download.default_directory": download_dir, 
        "download.prompt_for_download": False,       
        "download.directory_upgrade": True,         
        "safebrowsing.enabled": True                
    }

    options= ChromeOptions()
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    options.add_experimental_option("detach",True)
    options.add_experimental_option("prefs", prefs)

    driver= Chrome(options=options)
    sleep(5)
    driver.get(url=NEW_ONE)
    sleep(7)
    iframe = driver.find_element(By.TAG_NAME, "iframe")
    driver.switch_to.frame(iframe)
    element= driver.find_element(by=By.ID,value='tb2')
    element.click()
    archive= driver.find_element(by=By.XPATH,value='//*[@id="tblOCRV_wrapper"]/div[1]/button[3]') 
    archive.click()
    ruta_original = path.join(download_dir, "csv.csv")
    sleep(5)

    file= open(ruta_original,mode="r")
    if len(file.read().split(",")) < 10:
        print("Nah, is empty")
        file.close()
        remove(ruta_original)

    else:
        file.close()
        ruta_nueva = path.join(download_dir,new_name)
        sleep(5)
        rename(ruta_original, ruta_nueva)

    driver.quit()
scraping()
