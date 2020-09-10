# -*- coding: utf-8 -*-

import requests
from pprint import pprint
from bs4 import BeautifulSoup as bfs
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

host_name = '192.168.1.35'
port_name = 61290
hh_link = 'https://hh.ru/'
db_name = 'vacancy'
collection_name = 'hh_ru'
db_user = 'vacancy'
db_pwd = 'vacancy!'


def insert_db(db, coll_name, vacancy_list):

    for j in vacancy_list:
        if not db[coll_name].find_one(j):
            db[coll_name].insert_one(j)


def find_vacancy(db, coll_name, currency_, *args):

    document = db[coll_name].find({'salary.currency': currency_})

    for z in document:
        try:
            if len(args) == 1:
                if z['salary']['maximum'] != u'нет сведений':
                    if args[0] < z['salary']['maximum']:
                        z.pop('_id')
                        pprint(z)
                elif int(z['salary']['minimum']) < args[0] < int(z['salary']['maximum']):
                    z.pop('_id')
                    pprint(z)
            elif len(args) == 2:
                if z['salary']['maximum'] != u'нет сведений':
                    if args[0] < z['salary']['maximum'] and args[1] < z['salary']['maximum']:
                        z.pop('_id')
                        pprint(z)
                elif args[0] > args[1]:
                    if args[1] > int(z['salary']['minimum']) and args[0] < int(z['salary']['maximum']):
                        z.pop('_id')
                        pprint(z)
                elif args[0] < args[1]:
                    if args[0] > int(z['salary']['minimum']) and args[1] < int(z['salary']['maximum']):
                        z.pop('_id')
                        pprint(z)
                else:
                    if int(z['salary']['minimum']) < args[0] < int(z['salary']['maximum']):
                        z.pop('_id')
                        pprint(z)
            else:
                raise AttributeError('Недопустимое кличество аргументов')

        except TypeError:
            pass
        except ValueError:
            pass


try:
    client = MongoClient(host_name, port_name,
                         username=db_user,
                         password=db_pwd,
                         authSource=db_name,
                         authMechanism="SCRAM-SHA-1",
                         connect=True)
    data_base = client[db_name].command("ismaster")

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

    data_base = client[db_name]

    insert_db(data_base, collection_name, vacancy)

    find_vacancy(data_base, collection_name, 'руб.', 200000, 250000)

except ConnectionFailure:
    print(u'Сервер MongoDB не доступен')
