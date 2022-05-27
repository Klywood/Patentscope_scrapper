import logging
import time
from typing import Union, Optional, List, Any
import csv

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions as EC

#  disable webdriver-manager logs
logging.getLogger('WDM').setLevel(logging.NOTSET)


class PatentscopeSearch:

    def __init__(self):
        self.total_collected = 0

    def start(self, limit=1):
        with webdriver.Chrome(service=Service(ChromeDriverManager().install())) as browser:
            browser.get("https://patentscope.wipo.int/search/ru/search.jsf")
            #  wait for page load
            WebDriverWait(browser, 5).until(
                EC.presence_of_element_located((By.XPATH, r'//*[@id="simpleSearchForm:fpSearch"]')))
            #  click main search button
            btn = browser.find_element(By.XPATH,
                                       r'/html/body/div[2]/div[5]/div/div[2]/form/div/div[1]/div[2]/div/div/div[1]/div[2]/button')
            btn.click()
            self.switch_results_display_parameters(browser)
            while self.total_collected < limit:
                self.collect_data(browser)

    @staticmethod
    def switch_results_display_parameters(browser, num: Union[int, str] = 200):
        num = str(num)
        if num not in ['10', '50', '100', '200']:
            raise ValueError('Possible values are: 10, 50, 100, 200')
        #  switching number of results at page
        select = Select(browser.find_element(By.XPATH, '//*[@id="resultListCommandsForm:perPage:input"]'))
        select.select_by_visible_text(num)
        #  switching the sorting type that results will be displayed
        select = Select(browser.find_element(By.XPATH, '//*[@id="resultListCommandsForm:sort:input"]'))
        select.select_by_visible_text('Даты публикации по убыванию')
        #  wait until page load
        WebDriverWait(browser, 7).until(
            lambda x: len(x.find_elements(By.CLASS_NAME, 'ps-patent-result')) > 10)

    def collect_data(self, browser):
        patents = browser.find_elements(By.CLASS_NAME, 'trans-section')
        titles = map(lambda x: x.text, patents[::2])
        abstracts = map(lambda x: x.text, patents[1::2])
        links = map(lambda x: x.get_attribute('href'), browser.find_elements(By.CSS_SELECTOR, '.ps-patent-result--title a'))
        dates = map(lambda x: x.text, browser.find_elements(By.CSS_SELECTOR, '.ps-patent-result--title--ctr-pubdate span:nth-child(3)'))
        patent_class = map(lambda x: x.text, browser.find_elements(By.CSS_SELECTOR, '.ps-patent-result--ipc span:nth-child(1) span a'))
        applicants = map(lambda x: x.text, browser.find_elements(By.CLASS_NAME, 'ps-patent-result--applicant'))
        inventors = map(lambda x: x.text, browser.find_elements(By.CLASS_NAME, 'ps-patent-result--inventor'))

        with open('some.csv', 'w', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['title', 'abstract', 'link', 'publication_date', 'patent_class', 'applicant', 'inventor'])
            writer.writerows(zip(titles, abstracts, links, dates, patent_class, applicants, inventors))
        self.total_collected += 200
        print(self.total_collected)

        # print(titles[0].text)
        # print(abstracts[0].text)
        # print(links[0].get_attribute('href'))
        # print(dates[0].text)
        # print(patent_class[0].text)
        # print(applicants[0].text)
        # print(inventors[0].text)

    # def save_data(self):
    #     import csv
    #
    #     with open('some.csv', 'w') as f:
    #         writer = csv.writer(f)
    #         writer.writerows(zip(bins, frequencies))
    #     self.total_collected += 1


if __name__ == '__main__':
    beg = time.time()
    patent = PatentscopeSearch()
    patent.start()

    print(time.time() - beg)
