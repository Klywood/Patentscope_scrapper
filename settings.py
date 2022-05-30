
#  SELECTORS
#  num results per page selector (Xpath)
main_page_selector = r'//*[@id="simpleSearchForm:fpSearch"]'
#  search_button selector (Xpath)
search_button_selector = r'/html/body/div[2]/div[5]/div/div[2]/form/div/div[1]/div[2]/div/div/div[1]/div[2]/button'
#  num results per page selector (Xpath)
per_page_selector = '//*[@id="resultListCommandsForm:perPage:input"]'
#  how to sort results selector (Xpath)
sort_by_selector = '//*[@id="resultListCommandsForm:sort:input"]'
#  patents title and abstract selector (Class name)
patents_selector = 'trans-section'
#  patent's links selector (CSS_selector)
links_selector = '.ps-patent-result--title a'
#  publish dates selector (CSS_selector)
dates_selector = '.ps-patent-result--title--ctr-pubdate span:nth-child(3)'
#  patent's class selector (CSS_selector)
class_selector = '.ps-patent-result--ipc span:nth-child(1) span a'
#  patent's applicant selector (Class_name)
applicants_selector = 'ps-patent-result--applicant'
#  patent's inventors selector (Class_name)
inventors_selector = 'ps-patent-result--inventor'


