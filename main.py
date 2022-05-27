import logging
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions as EC

#  disable webdriver-manager logs
logging.getLogger('WDM').setLevel(logging.NOTSET)

def start():
    with webdriver.Chrome(service=Service(ChromeDriverManager().install())) as browser:
        browser.get("https://patentscope.wipo.int/search/ru/search.jsf")
        #  wait for page load
        WebDriverWait(browser, 5).until(
            EC.presence_of_element_located((By.XPATH, r'//*[@id="simpleSearchForm:fpSearch"]')))
        #  click main search button
        btn = browser.find_element(By.XPATH, r'/html/body/div[2]/div[5]/div/div[2]/form/div/div[1]/div[2]/div/div/div[1]/div[2]/button')
        btn.click()
        #  switch number of results at page to maximum - 200
        select = Select(browser.find_element(By.XPATH, '//*[@id="resultListCommandsForm:perPage:input"]'))
        select.select_by_visible_text('200')
        #  wait until page load
        WebDriverWait(browser, 7).until(
            lambda x: len(x.find_elements(By.CLASS_NAME, 'ps-patent-result')) > 10)
        print(len(browser.find_elements(By.CLASS_NAME, 'ps-patent-result')))


if __name__ == '__main__':
    beg = time.time()
    start()
    print(time.time() - beg)
