# -*- coding: utf-8 -*-

import requests
import pandas as pd
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

a_button = html_for_parsing.find_all('a', {'class': 'bloko-button'})

count_page = int(a_button[len(a_button) - 2].getText())

vacancy = list()

salary = dict()

for page in range(count_page):
    params['page'] = page
    html_hh = requests.get(hh_link + 'search/vacancy', headers=header, params=params)
    html_for_parsing = bfs(html_hh.text, 'html.parser')
    div_class_vacancy = html_for_parsing.find_all('div', {'class': 'vacancy-serp-item'})

    for i in div_class_vacancy:
        info_about_vacancy = {}
        salary = {}
        a_href = i.find('a').getText()
        info_about_vacancy['vacancy name'] = a_href

        a_href_vacancy = i.find('a').get('href')
        info_about_vacancy['vacancy link'] = a_href_vacancy

        list_span = i.find_all('span', {'class': 'bloko-section-header-3'})

        try:
            list_for_pars = list_span[1].getText().replace('\xa0', '').split()

            if len(list_for_pars) == 2:
                salary['minimum'] = int(list_for_pars[0].split('-')[0])
                salary['maximum'] = int(list_for_pars[0].split('-')[1])
                salary['currency'] = list_for_pars[1]
                info_about_vacancy['salary'] = salary

            elif len(list_for_pars) == 3:
                if list_for_pars[0] == u'от':
                    salary['minimum'] = int(list_for_pars[1])
                    salary['maximum'] = u'нет сведений'
                    salary['currency'] = list_for_pars[2]
                else:
                    salary['minimum'] = u'нет сведений'
                    salary['maximum'] = int(list_for_pars[1])
                    salary['currency'] = list_for_pars[2]
            info_about_vacancy['salary'] = salary

        except IndexError:
            info_about_vacancy['salary'] = u'нет сведений о заработной плате'
        try:
            a_href_info_suite = i.find('a', {'class': 'bloko-link_secondary'}).getText()
            info_about_vacancy['suite_info'] = a_href_info_suite
        except AttributeError:
            info_about_vacancy['suite_info'] = 'нет информации'

        list_span_city = i.find('span', {'class': 'vacancy-serp-item__meta-info'}).getText()
        info_about_vacancy['city'] = list_span_city

        vacancy.append(info_about_vacancy)

info_parsing = pd.DataFrame(vacancy)
info_parsing.to_csv('Parsing_html_bs/python_vacancy_hh.csv', index=False)
