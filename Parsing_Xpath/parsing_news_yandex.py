# -*- coding: utf-8 -*-

import requests
from datetime import datetime
from lxml import html
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, OperationFailure

host_name = '192.168.1.35'
port_name = 61290
yandex_news_link = 'https://yandex.ru/news'
db_name = 'news'
collection_name = 'yandex_news'
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

    yandex_ = requests.get(yandex_news_link, headers=header)

    dom_yandex_news = html.fromstring(yandex_.text)
    yandex_news = dom_yandex_news.xpath("//article[@class='mg-card news-card news-card_single "
                                        "news-card_type_image mg-grid__item mg-grid__item_type_card'] | "
                                        "//article[@class='mg-card news-card news-card_half news-card_type_image "
                                        "mg-grid__item mg-grid__item_type_card mg-grid__item_size_half'] | "
                                        "//article[@class='mg-card news-card news-card_double "
                                        "news-card_type_image mg-grid__item mg-grid__item_type_card']")

    list_for_news = []

    for new_ in yandex_news:
        dict_for_new = {}

        new = new_.xpath(".//h2[@class='news-card__title']/text()")

        if new:
            new = new[0]
        else:
            continue
        new_href = new_.xpath(".//a[@class='news-card__link']/@href")

        if new_href:
            new_href = new_href[0]
        else:
            continue

        time_ = new_.xpath(".//span[@class='mg-card-source__time']/text()")
        source = new_.xpath(".//div[@class='mg-card-source news-card__source']/span/a/text()")
        dict_for_new['source'] = source[0]
        dict_for_new['new'] = new.replace('\xa0', ' ')
        dict_for_new['new_link'] = new_href
        dict_for_new['time'] = time_[0]
        dict_for_new['date'] = date_ = datetime.now().date().strftime("%m/%d/%Y")

        list_for_news.append(dict_for_new)

    data_base = client[db_name]

    insert_db(data_base, collection_name, list_for_news)

except ConnectionFailure:
    print(u'Сервер MongoDB не доступен')

except OperationFailure:
    print(u'некорректное имя пользователя или пароль')
