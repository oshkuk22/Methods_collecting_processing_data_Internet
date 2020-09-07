import requests
from bs4 import BeautifulSoup as bfs


hh_link = 'https://hh.ru/'

header = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) '
                        'Chrome/78.0.3904.108 YaBrowser/19.12.3.332 (beta) Yowser/2.5 Safari/537.36'}

params = {'clusters': 'true',
          'area': '1',
          'no_magic': 'true',
          'enable_snippets': 'true',
          'salary': '',
          'st': 'searchVacancy',
          'text': u'Python',
          'page': '0'}

html_hh = requests.get(hh_link + 'search/vacancy', headers=header, params=params)

html_for_parsing = bfs(html_hh.text, 'html.parser')

div_class_vacancy = html_for_parsing.find_all('div', {'class': 'vacancy-serp-item'})

info_about_vacancy = dict()
name_vacancy = list()
salary = list()
salary_all = dict()

for i in div_class_vacancy:
    a_href = i.find('a').getText()
    name_vacancy.append(a_href)
    # salary_value = i.findChildren(recursive=False)
    list_span = i.find_all('span', {'class': 'bloko-section-header-3'})
    try:
        salary.append(list_span[1].getText().replace('\xa0', '').split())
        # if len
    except IndexError:
        salary.append(['нет сведений о заработной плате'])
    # salary_value = i.find('div', {'class': 'bloko-section-header-3'})

print((salary))
