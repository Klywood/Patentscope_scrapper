
#  SELECTORS
#  search_button selector (XPATH)
search_button_selector = '//*[@id="simpleSearchForm:fpSearch:buttons"]/button'

#  num results per page selector (XPATH)
per_page_selector = '//*[@id="resultListCommandsForm:perPage:input"]'
#  how to sort results selector (XPATH)
sort_by_selector = '//*[@id="resultListCommandsForm:sort:input"]'

#  elements with patents info (CLASS_NAME)
patents_selector = 'ps-patent-result'
#  title selector
title_selector = '.ps-patent-result--first-row .trans-section'
#  abstracts selector
abstract_selector = '.ps-patent-result--second-row .trans-section'
#  patent's links selector (CSS_SELECTOR)
links_selector = '.ps-patent-result--first-row a'
#  publish dates selector (CSS_SELECTOR)
dates_selector = '.ps-patent-result--title--ctr-pubdate span:nth-child(3)'
#  patent's class selector (CSS_SELECTOR)
class_selector = '.ps-patent-result--second-row a'
#  patent's applicant selector (CLASS_NAME)
applicants_selector = '.ps-patent-result--second-row a'
#  patent's inventors selector (CLASS_NAME)
inventors_selector = '.ps-patent-result--inventor'
#  next_button selector (CSS_SELECTOR)
next_button_selector = '.js-paginator-next'


title = '.ps-patent-result--first-row .trans-section'
link = '.ps-patent-result--first-row a'
patent_class = '.ps-patent-result--second-row a'
applicant = '.ps-patent-result--applicant'
inventor = '.ps-patent-result--inventor'
date = '.ps-patent-result--title--ctr-pubdate span:nth-child(3)'
abstracts = '.ps-patent-result--second-row .trans-section'
