# -*- coding: utf-8 -*-

import requests
from lxml import html
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, OperationFailure

host_name = '192.168.1.35'
port_name = 61290
mail_news_link = 'https://news.mail.ru'
db_name = 'news'
collection_name = 'mail_news'
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

    header = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:80.0) Gecko/20100101 Firefox/80.0'}

    mail_ = requests.get(mail_news_link, headers=header)

    dom_mail_news = html.fromstring(mail_.text)

    mail_news = dom_mail_news.xpath("//table[@class = 'daynews__inner']//a/@href |"
                                    " //ul[@class='list list_type_square list_half js-module']/li[@class='list__item']"
                                    "//a/@href")
    list_for_news = []

    for link_ in mail_news:
        dict_for_new = {}
        new_ = requests.get(link_, headers=header)
        dom_mail_new = html.fromstring(new_.text)

        dict_for_new['link_new'] = link_
        dict_for_new['new'] = dom_mail_new.xpath("//h1/text()")[0]
        dict_for_new['source'] = dom_mail_new.xpath("//a[@class='link color_gray breadcrumbs__link']/span/text()")[0]
        dict_for_new['time'] = dom_mail_new.xpath("//span[@class='note__text breadcrumbs__text js-ago']/text()")[0]

        list_for_news.append(dict_for_new)

    data_base = client[db_name]

    insert_db(data_base, collection_name, list_for_news)

except ConnectionFailure:
    print(u'Сервер MongoDB не доступен')

except OperationFailure:
    print(u'некорректное имя пользователя или пароль')
