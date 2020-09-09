# -*- coding: utf-8 -*-

import requests
import pandas as pd
from bs4 import BeautifulSoup as bfs

superjob_link = 'https://www.superjob.ru'

header = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) '
                        'Chrome/78.0.3904.108 YaBrowser/19.12.3.332 (beta) Yowser/2.5 Safari/537.36'}

params = {'keywords': 'python',
          'geo[t][0]': '4',
          'page': '1'}

html_superjob = requests.get(superjob_link + '/vacancy/search', headers=header, params=params)

html_for_parsing = bfs(html_superjob.text, 'html.parser')

a_button = html_for_parsing.find_all('a', {'class': '_3ze9n'})

count_page = int(a_button[len(a_button) - 2].getText())

vacancy = list()

salary = dict()

for page in range(count_page):

    params['page'] = page
    html_superjob = requests.get(superjob_link + '/vacancy/search', headers=header, params=params)
    html_for_parsing = bfs(html_superjob.text, 'html.parser')
    div_class_vacancy = html_for_parsing.find_all('div', {'class': 'f-test-vacancy-item'})

    for i in div_class_vacancy:
        info_about_vacancy = {}
        salary = {}
        a_href = i.find('a').getText()
        info_about_vacancy['vacancy name'] = a_href

        a_href_vacancy = i.find('a').get('href')
        info_about_vacancy['vacancy link'] = superjob_link + a_href_vacancy

        list_span = i.find('span', {'class': '_2Wp8I'}).getText().split('\xa0')

        if len(list_span) == 1:
            info_about_vacancy['salary'] = list_span[0]

        elif len(list_span) == 4:
            if list_span[0] == u'от':
                salary['minimum'] = int(list_span[1] + list_span[2])
                salary['maximum'] = u'нет сведений'
                salary['currency'] = list_span[3]
                info_about_vacancy['salary'] = salary
            else:
                salary['minimum'] = u'нет сведений'
                salary['maximum'] = int(list_span[1] + list_span[2])
                salary['currency'] = list_span[3]
                info_about_vacancy['salary'] = salary
        elif len(list_span) == 3:
            salary['minimum'] = int(list_span[0] + list_span[1])
            salary['maximum'] = int(list_span[0] + list_span[1])
            salary['currency'] = list_span[2]
            info_about_vacancy['salary'] = salary
        else:
            salary['minimum'] = int(list_span[0] + list_span[1])
            salary['maximum'] = int(list_span[3] + list_span[4])
            salary['currency'] = list_span[5]
            info_about_vacancy['salary'] = salary

        try:
            a_href_info_suite = i.find('a', {'class': '_205Zx'}).getText()
            info_about_vacancy['suite_info'] = a_href_info_suite
        except AttributeError:
            info_about_vacancy['suite_info'] = 'нет информации'

        list_span_city = i.find('span', {'class': 'f-test-text-company-item-location'}).getText()
        info_about_vacancy['date of placement'] = str(list_span_city).split('•')[0]
        info_about_vacancy['city'] = str(list_span_city).split('•')[1]
        vacancy.append(info_about_vacancy)

print(hash({'a': 5, 'b': 'h'}))
info_parsing = pd.DataFrame(vacancy)
info_parsing.to_csv('Parsing_html_bs/python_vacancy_superjob.csv', index=False)
