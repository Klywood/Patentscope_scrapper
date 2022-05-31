import logging
import os
import time
# from typing import Union
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

    def __init__(self, headless: bool = True, page: int = 1, results_on_page=200):
        """Initialization method"""
        #  configure browser options
        self.__chrome_options = Options()
        self.__chrome_options.add_argument("--disable-extensions")
        self.__chrome_options.add_argument("--disable-gpu")
        #  disable the visual display of the browser
        self.__chrome_options.headless = headless
        #  start_page number
        self.__current_page = page
        #  results displayed at page
        self.__limit = results_on_page
        #  count args
        self.__collected = 0
        self.__total_collected = 0

    @property
    def limit(self):
        return self.__limit

    @limit.setter
    def limit(self, num):
        num = str(num)
        if num not in ['10', '50', '100', '200']:
            raise ValueError('Possible values are: 10, 50, 100, 200')
        self.__limit = num

    def start(self, limit: int = 200):
        """Main method"""
        with webdriver.Chrome(service=Service(ChromeDriverManager().install()),
                              options=self.__chrome_options) as browser:
            browser.get("https://patentscope.wipo.int/search/ru/search.jsf")
            #  load main page with results
            self.__search_results(browser)
            #  collect info about patents
            self.__collect_data(browser)
            while self.__total_collected < limit:
                #  go to next result page
                self.__current_page += 1
                self.__go_to_next_page(browser)
                #  collect_data
                self.__collect_data(browser)

    def __search_results(self, browser):
        """Method to display results"""
        #  wait for page to load
        WebDriverWait(browser, 5).until(
            EC.element_to_be_clickable((By.XPATH, st.search_button_selector)))
        #  click main search button
        btn = browser.find_element(By.XPATH, st.search_button_selector)
        btn.click()
        self.__wait_for_results(browser, 5)
        self.__switch_results_display_parameters(browser)

    def __switch_results_display_parameters(self, browser):
        """Set result parameters  display"""
        #  switching number of results at page
        select = Select(browser.find_element(By.XPATH, st.per_page_selector))
        select.select_by_visible_text(str(self.limit))
        #  switching the sorting type that results will be displayed
        select = Select(browser.find_element(By.XPATH, st.sort_by_selector))
        select.select_by_visible_text('Даты публикации по убыванию')

    @classmethod
    def __wait_for_results(cls, browser, results_on_page=5):
        """Waiting for the results to load"""
        #  wait until page load
        WebDriverWait(browser, 20).until(
            lambda x: len(x.find_elements(By.CSS_SELECTOR, '.ps-patent-result')) >= results_on_page)

    def __collect_data(self, browser):
        """Collect main info about patents"""
        #  wait for page loading
        self.__wait_for_results(browser, self.limit)
        #  collect data
        patents = browser.find_elements(By.CSS_SELECTOR, st.patents_selector)
        titles = [x.text for x in patents[::2]]
        abstracts = [x.text for x in patents[1::2]]
        links = [x.get_attribute('href') for x in browser.find_elements(By.CSS_SELECTOR, st.links_selector)]
        dates = [x.text for x in browser.find_elements(By.CSS_SELECTOR, st.dates_selector)]
        patent_classes = [x.text for x in browser.find_elements(By.CSS_SELECTOR, st.class_selector)]
        applicants = [x.text for x in browser.find_elements(By.CLASS_NAME, st.applicants_selector)]
        inventors = [x.text for x in browser.find_elements(By.CLASS_NAME, st.inventors_selector)]
        print(len(browser.find_elements(By.CSS_SELECTOR, st.class_selector)))
        print(len(titles), len(abstracts), len(links), len(dates), len(patent_classes), len(applicants), len(inventors))
        #  convert to specified format
        data = self.__convert_data(links, titles, applicants, inventors,
                                   dates, abstracts, patent_classes)
        #  save to csv
        self.__save_data(data)

    def __convert_data(self, links: list, titles: list, applicants: list,
                       inventors: list, dates: list, abstracts: list, patent_classes: list):
        """Convert data to specified format:

            ('type', 'language', 'url', 'title', 'creators', 'publication_name',
            'publication_date', 'abstract', 'keywords')
        """
        self.__collected = len(titles)
        data = [('Patent', None, links[i], titles[i],
                 applicants[i], inventors[i], dates[i], abstracts[i],
                 self.create_keywords(patent_classes[i]))
                for i in range(self.__collected)]
        return data

    @staticmethod
    def create_keywords(patent_class):
        """Converting patent_class to keywords"""
        #  TODO обработка международной патентной классификации в ключевые слова
        # keywords = []
        a, b = patent_class.split()
        return [a, b]

    def __save_data(self, data, filename='patents.csv'):
        """Save data to csv-file"""
        with open(filename, 'a', encoding='utf-8') as file:
            writer = csv.writer(file)
            #  TODO if file is empty - write labels (как проверить пустой ли файл)
            if os.stat(filename).st_size == 0:
                writer.writerow(
                    ['type', 'language', 'url', 'title', 'creators',
                     'publication_name', 'publication_date', 'abstract', 'keywords'])
            writer.writerows(data)
        self.__total_collected += self.__collected
        print('saved:', self.__total_collected)

    def __go_to_next_page(self, browser):
        """Switch page to upload more patents"""
        next_button = browser.find_element(By.CSS_SELECTOR, st.next_button_selector)
        next_button.click()
        WebDriverWait(browser, 20).until(EC.text_to_be_present_in_element((By.ID, r'resultListCommandsForm:pageNumber'),
                                                                         str(self.__current_page)))
        print('switched!')


if __name__ == '__main__':
    since = time.time()

    patent = PatentscopeSearch(False)
    patent.start(1000)
    # patent.create_keywords('G01N 1/16')

    # with webdriver.Chrome(service=Service(ChromeDriverManager().install())) as browser:
    #     browser.get("https://patentscope.wipo.int/search/ru/search.jsf")
    #     WebDriverWait(browser, 5).until(
    #         EC.presence_of_element_located((By.XPATH, st.main_page_selector)))
    #     #  click main search button
    #     btn = browser.find_element(By.XPATH, st.search_button_selector)
    #     btn.click()
    #     time.sleep(5)
    #     res = browser.find_element(By.CSS_SELECTOR, '.ps-patent-result')
    #
    #     print(res.find_element(By.CSS_SELECTOR, st.link).get_attribute('href'))
    #     print(res.find_element(By.CSS_SELECTOR, st.title).text)
    #     print(res.find_element(By.CSS_SELECTOR, st.date).text)
    #     print(res.find_element(By.CSS_SELECTOR, st.inventor).text)
    #     print(res.find_element(By.CSS_SELECTOR, st.applicant).text)
    #     print(res.find_element(By.CSS_SELECTOR, st.patent_class).text)
    #     print(res.find_element(By.CSS_SELECTOR, st.abstracts).text)


    print(time.time() - since)
