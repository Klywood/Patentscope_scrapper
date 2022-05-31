import logging
import os
import sys
import time
import concurrent.futures
import csv
import datetime
from typing import Union

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
        #  attribute to store elements with info about patents
        self.__patents = None
        #  start_page number
        self.__current_page = page
        #  results displayed at page
        self.__limit = results_on_page
        #  count args
        self.__collected = 0
        self.__total_collected = 0
        #  create logger
        self._logger = self.create_logger()

    @staticmethod
    def create_logger(folder_name: str = st.LOG_FOLDER):
        """Creates logger

        Parameters:
            folder_name: folder name or path to the folder to store log-file

        Returns:
            logger with settings and handlers
        """
        #  create folder
        os.makedirs(folder_name, exist_ok=True)
        #  creating full path to log-file
        full_name = os.path.join(folder_name, 'patentscope_search.log')
        #  creating new logger
        logger = logging.getLogger(st.LOG_NAME)
        #  set the logger level, messages which are less severe than level will be ignored
        logger.setLevel(st.LOG_LEVEL)
        # set format of messages
        log_format = logging.Formatter('%(asctime)s: %(levelname)s: %(name)s: %(message)s',
                                       "%Y-%m-%d %H:%M:%S")
        #  create handlers
        filehandler = logging.FileHandler(full_name, 'a')
        filehandler.setLevel(st.FH_level)
        filehandler.setFormatter(log_format)
        streamhandler = logging.StreamHandler(stream=sys.stdout)
        streamhandler.setLevel(st.SH_level)
        streamhandler.setFormatter(log_format)
        #  add handlers to logger
        logger.addHandler(filehandler)
        logger.addHandler(streamhandler)
        #  first message in new logger
        logger.debug('Logger created!')

        return logger

    @property
    def limit(self):
        """Getter for limit attribute"""
        return self.__limit

    @limit.setter
    def limit(self, num: Union[int, str]):
        """Setter for limit attribute"""
        num = str(num)
        if num not in ['10', '50', '100', '200']:
            raise ValueError('Incorrect limit. Possible values are: 10, 50, 100, 200')
        self.__limit = num

    def start(self, limit: int = 200, filename='patents'):
        """Main method"""
        file_to_save = f"{filename}_{str(datetime.datetime.now().strftime('%d-%m-%Y'))}.csv"
        start_time = time.time()
        with webdriver.Chrome(service=Service(ChromeDriverManager().install()),
                              options=self.__chrome_options) as browser:
            browser.get("https://patentscope.wipo.int/search/ru/search.jsf")
            #  load main page with results
            self.__search_results(browser)
            while self.__total_collected < limit:
                #  collect_data
                data = self.__collect_data(browser)
                #  save to file
                self.__save_collected(data, file_to_save)
                self._logger.info(f"Successfully saved {self.__total_collected} of {limit} patents.\n"
                                  f"{round(self.__total_collected/limit, 2) * 100} % completed!\n"
                                  f"Total work time: {str(datetime.timedelta(seconds=round(time.time() - start_time)))}")
                #  go to next result page
                self.__current_page += 1
                self.__go_to_next_page(browser)
            self._logger.info(f"{self.__total_collected} patents saved to file. End of work")

    def __search_results(self, browser):
        """Method to display results"""
        #  wait for page to load
        WebDriverWait(browser, 5).until(
            EC.element_to_be_clickable((By.XPATH, st.search_button_selector)))
        #  click main search button
        btn = browser.find_element(By.XPATH, st.search_button_selector)
        btn.click()
        self._logger.debug('Waiting for results...')
        self.__wait_for_results(browser)
        self.__switch_results_display_parameters(browser)

    def __switch_results_display_parameters(self, browser):
        """Configuring the display parameters of the results"""
        self._logger.debug("Configuring the display parameters of the results...")
        #  switching number of results at page
        select = Select(browser.find_element(By.XPATH, st.per_page_selector))
        select.select_by_visible_text(str(self.limit))
        #  switching the sorting type that results will be displayed
        select = Select(browser.find_element(By.XPATH, st.sort_by_selector))
        select.select_by_visible_text('Даты публикации по убыванию')

    def __wait_for_results(self, browser, results_on_page=5):
        """Waiting for the results to load"""
        #  wait until page load
        WebDriverWait(browser, 20).until(
            lambda x: len(x.find_elements(By.CSS_SELECTOR, '.ps-patent-result')) >= results_on_page)
        self._logger.debug('Page successfully loaded!')

    def __collect_data(self, browser, workers: int = 24) -> list:
        """Collect main info about patents
        Parameters:
            workers: number of threads

        Returns:
            list with summary information about patents (tuples)
        """
        self._logger.debug("Collecting summary information about patents...")
        res = []
        #  wait for page loading
        self.__wait_for_results(browser, self.limit)

        #  collect main elements with patent's info
        self.__patents = browser.find_elements(By.CSS_SELECTOR, st.patents_selector)
        self._logger.debug(f"{len(self.__patents)} patents found")

        #  get summary information about patents in multithreading mode
        with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
            #  creating list of futures
            future_to_url = [executor.submit(self.__get_all_data_from_element, element) for element in self.__patents]
            for future in concurrent.futures.as_completed(future_to_url):
                res.append(future.result())

        self.__collected = len(res)
        self._logger.debug(f"Summary information about {self.__collected} patents successfully collected")
        return res

    def __get_all_data_from_element(self, element):
        """Collect summary information from patent's selenium_element"""
        res = ('Patent',  # type
               None,  # language
               self.__get_content_from_element(element, st.links_selector, 'href'),  # url
               self.__get_content_from_element(element, st.title_selector),  # title
               self.__get_content_from_element(element, st.inventors_selector),  # creators
               self.__get_content_from_element(element, st.applicants_selector),  # source/applicant
               self.__get_content_from_element(element, st.dates_selector),  # publication_date
               self.__get_content_from_element(element, st.abstract_selector),  # abstract
               self.create_keywords(self.__get_content_from_element(element, st.class_selector))  # keywords
               )
        return res

    @staticmethod
    def __get_content_from_element(element, selector, content_type='text'):
        """Find content from element by CSS_SELECTOR"""
        res = element.find_elements(By.CSS_SELECTOR, selector)
        #  if no element found
        if len(res) == 0:
            return None
        if content_type == 'text':
            return res[0].text
        elif content_type == 'href':
            return res[0].get_attribute('href')
        else:
            raise ValueError('Incorrect content_type. Possible values are: "text", "href"')

    @staticmethod
    def create_keywords(patent_class):
        """Converting patent_class to keywords"""
        #  TODO обработка международной патентной классификации в ключевые слова
        if not patent_class:
            return None
        a, b = patent_class.split()
        return [a, b]

    def __save_collected(self, data, filename='patents.csv'):
        """Save data to csv-file"""
        with open(filename, 'a', encoding='utf-8') as file:
            writer = csv.writer(file)
            #  if file is empty - write labels
            if os.stat(filename).st_size == 0:
                writer.writerow(
                    ['type', 'language', 'url', 'title', 'creators',
                     'source/applicant', 'publication_date', 'abstract', 'keywords'])
            writer.writerows(data)
        self.__total_collected += self.__collected

    def __go_to_next_page(self, browser):
        """Switch page to upload more patents"""
        #  find and click 'next page' button
        next_button = browser.find_element(By.CSS_SELECTOR, st.next_button_selector)
        next_button.click()
        #  wait until page load
        WebDriverWait(browser, 20).until(EC.text_to_be_present_in_element((By.ID, r'resultListCommandsForm:pageNumber'),
                                                                          str(self.__current_page)))
        self._logger.debug(f"Switched to {self.__current_page} page")


if __name__ == '__main__':

    patent = PatentscopeSearch(True)
    patent.start(2000)
