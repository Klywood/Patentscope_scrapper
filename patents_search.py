import logging
import time
from typing import Union
import csv

import settings as st
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions as EC

#  disable webdriver-manager logs
logging.getLogger('WDM').setLevel(logging.NOTSET)


class PatentscopeSearch:
    """Class to save info about patents from https://patentscope.wipo.int"""

    def __init__(self, headless: bool = True):
        """Initialization method"""
        #  configure browser options
        self.__chrome_options = Options()
        self.__chrome_options.add_argument("--disable-extensions")
        self.__chrome_options.add_argument("--disable-gpu")
        #  disable the visual display of the browser
        self.__chrome_options.headless = headless
        #  count args
        self.__collected = 0
        self.__total_collected = 0

    def start(self, limit: int = 200):
        """Main method"""
        with webdriver.Chrome(service=Service(ChromeDriverManager().install()),
                              options=self.__chrome_options) as browser:
            browser.get("https://patentscope.wipo.int/search/ru/search.jsf")
            #  load main page with results
            self.__search_results()
            #  collect info about patents
            while self.__total_collected < limit:
                #  collect_data
                self.__collect_data(browser)
                #  go to next result page
                self.__go_to_next_page(browser)

    def __search_results(self, browser):
        """Method to display results"""
        #  wait for page to load
        WebDriverWait(browser, 5).until(
            EC.presence_of_element_located((By.XPATH, st.main_page_selector)))
        #  click main search button
        btn = browser.find_element(By.XPATH, st.search_button_selector)
        btn.click()
        self.__switch_results_display_parameters(browser)

    @classmethod
    def __switch_results_display_parameters(cls, browser, num: Union[int, str] = 200):
        """Set result parameters  display"""
        num = str(num)
        if num not in ['10', '50', '100', '200']:
            raise ValueError('Possible values are: 10, 50, 100, 200')
        #  switching number of results at page
        select = Select(browser.find_element(By.XPATH, st.per_page_selector))
        select.select_by_visible_text(num)
        #  switching the sorting type that results will be displayed
        select = Select(browser.find_element(By.XPATH, st.sort_by_selector))
        select.select_by_visible_text('Даты публикации по убыванию')
        #  wait until page load
        WebDriverWait(browser, 7).until(
            lambda x: len(x.find_elements(By.CLASS_NAME, 'ps-patent-result')) > 10)

    def __collect_data(self, browser):
        """Collect main info about patents"""
        patents = browser.find_elements(By.CLASS_NAME, st.patents_selector)
        titles = map(lambda x: x.text, patents[::2])
        abstracts = map(lambda x: x.text, patents[1::2])
        links = map(lambda x: x.get_attribute('href'), browser.find_elements(By.CSS_SELECTOR, st.links_selector))
        dates = map(lambda x: x.text, browser.find_elements(By.CSS_SELECTOR, st.dates_selector))
        patent_class = map(lambda x: x.text, browser.find_elements(By.CSS_SELECTOR, st.class_selector))
        applicants = map(lambda x: x.text, browser.find_elements(By.CLASS_NAME, st.applicants_selector))
        inventors = map(lambda x: x.text, browser.find_elements(By.CLASS_NAME, st.inventors_selector))
        #  zip collect_data
        data = zip(titles, abstracts, links, dates, patent_class, applicants, inventors)
        self.__collected = len(list(titles))
        #  save to csv
        self.__save_data(data)
        
    def __save_data(self, data, filename='some.csv'):
        """Save data to csv-file"""
        with open(filename, 'a', encoding='utf-8') as file:
            writer = csv.writer(file)
            #  TODO if file is empty - write labels (как проверить пустой ли файл)
            if self.__total_collected == 0:
                writer.writerow(
                    ['title', 'abstract', 'link', 'publication_date', 'patent_class', 'applicant', 'inventor'])
            writer.writerows(data)
        self.__total_collected += self.__collected
        print(self.__total_collected)

    def __go_to_next_page(self, browser):
        """Switch page to upload more patents"""
        pass


if __name__ == '__main__':
    since = time.time()

    patent = PatentscopeSearch()
    patent.start()

    print(time.time() - since)
