# -*- coding: utf-8 -*-

import requests
from datetime import datetime, timedelta
from lxml import html
from pprint import pprint
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, OperationFailure

host_name = '192.168.1.35'
port_name = 61290
lenta_link = 'https://lenta.ru'
db_name = 'news'
collection_name = 'lenta'
db_user = 'news'
db_pwd = 'news!'


def insert_db(db, coll_name, news_list):

    for news_ in news_list:
        db[coll_name].update_one(news_, {'$set': news_}, upsert=True)


try:
    client = MongoClient(host_name, port_name,
                         username=db_user,
                         password=db_pwd,
                         authSource=db_name,
                         authMechanism="SCRAM-SHA-1",
                         connect=True)

    data_base = client[db_name].command("ismaster")

    header = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:80.0) Gecko/20100101 Firefox/80.0'}

    lenta_ = requests.get(lenta_link + '/rubrics/science/', headers=header)

    dom_lenta = html.fromstring(lenta_.text)
    pprint(dom_lenta)
    lenta_news = dom_lenta.xpath("//div[@class='span4']/section/div")

    list_for_news = []

    for new_ in lenta_news:
        dict_for_new = {}

        new = new_.xpath(".//div[@class='titles']/h3/a/span/text()")

        if new:
            new = new[0]
        else:
            continue
        new_href = new_.xpath(".//div[@class='titles']/h3/a/@href")

        if new_href:
            new_href = new_href[0]
        else:
            continue

        time_ = new_.xpath(".//div[@class='info g-date item__info']/span/span/text()")[0]
        date_ = new_.xpath(".//div[@class='info g-date item__info']/span/text()")[0]

        dict_for_new['source'] = 'lenta ru'
        dict_for_new['new'] = new.replace('\xa0', ' ')
        dict_for_new['new_link'] = lenta_link + new_href
        dict_for_new['time'] = time_

        if date_ == u'Сегодня':
            date_ = datetime.now().date().strftime("%m/%d/%Y")
        elif date_ == u'Вчера':
            date_ = (datetime.now().date() - timedelta(days=1)).strftime("%m/%d/%Y")
        else:
            dict_for_new['date'] = date_
        list_for_news.append(dict_for_new)

    data_base = client[db_name]

    insert_db(data_base, collection_name, list_for_news)

except ConnectionFailure:
    print(u'Сервер MongoDB не доступен')

except OperationFailure:
    print(u'некорректное имя пользователя или пароль')
