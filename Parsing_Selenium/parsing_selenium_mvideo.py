# -*- coding: utf-8 -*-

import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, OperationFailure

host_name = '192.168.1.35'
port_name = 61290
db_name = 'se_parsing'

collection_name = 'mvideo'
db_user = 'se_parsing'
db_pwd = 'se_parsing!'

INFO_PRODUCTS = set()
LIST_FIND = list()
LINK_MVIDEO = 'https://www.mvideo.ru/'
CHROME_SIZE = Options()
CHROME_SIZE.add_argument('start-maximized')

CHROME_DRIVER = webdriver.Chrome(executable_path='/media/oshkuk/Data/workspace/geekbrains/'
                                                 'Methods_collecting_processing_data_Internet/'
                                                 'Parsing_Selenium/chromedriver', options=CHROME_SIZE)

CHROME_DRIVER.get(LINK_MVIDEO)


def insert_db(db, coll_name, mail_list):
    for mail in mail_list:
        db[coll_name].update_one(mail, {'$set': mail}, upsert=True)


def find_link_mail():
    a_info_product = CHROME_DRIVER.find_elements_by_xpath('(//div[@class="gallery-layout sel-hits-block "])[2]'
                                                          '//a[@class="sel-product-tile-title"]')
    for info in a_info_product:
        info_ = info.get_attribute('data-product-info')
        href_ = info.get_attribute('href')
        if info_:
            info_ = info_.replace('\n\t\t\t\t\t', '').replace('}', ',') + '"' + 'link"' + ':' + '"' + href_ + '"' '}'
            INFO_PRODUCTS.add(info_)
    return INFO_PRODUCTS


def scrolling(time_sleep):
    time.sleep(time_sleep)

    scroll = CHROME_DRIVER.find_element_by_xpath('(//div[@class="gallery-layout sel-hits-block "])[2]'
                                                 '//a[contains(@class,"next-btn")]')
    if 'disabled' in scroll.get_attribute('class'):
        return True
    else:
        scroll.click()


try:
    client = MongoClient(host_name, port_name,
                         username=db_user,
                         password=db_pwd,
                         authSource=db_name,
                         authMechanism="SCRAM-SHA-1",
                         connect=True)

    data_base = client[db_name].command("ismaster")

    WebDriverWait(CHROME_DRIVER, 10).until(ec.title_contains('М.Видео - интернет-магазин цифровой и '
                                                             'бытовой техники и электроники, низкие цены,'
                                                             ' большой каталог, отзывы. - Москва'))

    while True:
        time.sleep(3)
        hits_product = find_link_mail()
        sc = scrolling(2)
        if sc:
            break
    for i in INFO_PRODUCTS:
        dict_find = dict()
        dict_find = {'product_name': eval(i)['productName'], 'product_category': eval(i)['productCategoryName'],
                     'price': eval(i)['productPriceLocal'], 'vendor': eval(i)['productVendorName'],
                     'link': eval(i)['link']}
        LIST_FIND.append(dict_find)

    CHROME_DRIVER.close()

    data_base = client[db_name]

    insert_db(data_base, collection_name, LIST_FIND)

except ConnectionFailure:
    print(u'Сервер MongoDB не доступен')

except OperationFailure:
    print(u'некорректное имя пользователя или пароль')
