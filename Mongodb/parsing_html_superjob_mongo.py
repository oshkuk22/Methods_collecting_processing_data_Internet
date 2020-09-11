# -*- coding: utf-8 -*-

import requests
from pprint import pprint
from bs4 import BeautifulSoup as bfs
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

host_name = '192.168.1.35'
port_name = 61290
superjob_link = 'https://www.superjob.ru'
db_name = 'vacancy'
collection_name = 'superjob_ru'
db_user = 'vacancy'
db_pwd = 'vacancy!'


def insert_db(db, coll_name, vacancy_list):

    for vacancy_ in vacancy_list:
        db[coll_name].update_one(vacancy_, {'$set': vacancy_}, upsert=True)


def find_vacancy(db, coll_name, currency_, *args):

    for vacancy_ in db[coll_name].find({'$and': [{'salary.currency': {'$eq': currency_}},
                                                 {'$or': [{'salary.minimum': {'$gt': args[0]}},
                                                          {'salary.maximum': {'$gt': args[0]}}]}]}):
        vacancy_.pop('_id')
        pprint(vacancy_)


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

    data_base = client[db_name]

    insert_db(data_base, collection_name, vacancy)

    find_vacancy(data_base, collection_name, 'руб.', 180000)

except ConnectionFailure:
    print(u'Сервер MongoDB не доступен')
