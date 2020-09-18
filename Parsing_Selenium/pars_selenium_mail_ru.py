# -*- coding: utf-8 -*-
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.action_chains import ActionChains
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, OperationFailure

host_name = '192.168.1.35'
port_name = 61290
db_name = 'se_parsing'
collection_name = 'mailru'
db_user = 'se_parsing'
db_pwd = 'se_parsing!'

FOR_EQUAL = 0
HREF_MAIL = set()
LIST_MAIL = []
LINK_MAIL = 'https://mail.ru/'
CHROME_SIZE = Options()
CHROME_SIZE.add_argument('start-maximized')

CHROME_DRIVER = webdriver.Chrome(executable_path='/media/oshkuk/Data/workspace/geekbrains/'
                                                 'Methods_collecting_processing_data_Internet/'
                                                 'Parsing_Selenium/chromedriver', options=CHROME_SIZE)

CHROME_DRIVER.get(LINK_MAIL)


def insert_db(db, coll_name, mail_list):

    for mail in mail_list:
        db[coll_name].update_one(mail, {'$set': mail}, upsert=True)


def find_link_mail():
    a_href_email = CHROME_DRIVER.find_elements_by_class_name("js-letter-list-item")

    for link in a_href_email:
        HREF_MAIL.add(link.get_attribute('href'))

    return a_href_email


def entered_mail(login_, password_, *args):
    login = CHROME_DRIVER.find_element_by_id(args[0])
    login.send_keys(login_)

    button_input_password = CHROME_DRIVER.find_element_by_class_name(args[1])
    button_input_password.submit()

    time.sleep(1)

    password = CHROME_DRIVER.find_element_by_id(args[2])
    password.send_keys(password_)

    button_submit_password = CHROME_DRIVER.find_element_by_class_name(args[1])
    button_submit_password.submit()


def scrolling(time_sleep):
    time.sleep(time_sleep)

    element_for_scrolling = find_link_mail()

    scrolling_action = ActionChains(CHROME_DRIVER)
    scrolling_action.move_to_element(element_for_scrolling[-1])
    scrolling_action.perform()


try:
    client = MongoClient(host_name, port_name,
                         username=db_user,
                         password=db_pwd,
                         authSource=db_name,
                         authMechanism="SCRAM-SHA-1",
                         connect=True)

    data_base = client[db_name].command("ismaster")
    entered_mail('study.ai_172@mail.ru', 'NextPassword172',
                 'mailbox:login-input', 'o-control', 'mailbox:password-input')

    WebDriverWait(CHROME_DRIVER, 10).until(ec.title_contains('Входящие - Почта Mail.ru'))

    while True:
        scrolling(1)

        if FOR_EQUAL == len(HREF_MAIL):
            break
        FOR_EQUAL = len(HREF_MAIL)

    for mail_ in HREF_MAIL:
        dict_for_mail = {}
        CHROME_DRIVER.get(mail_)

        time.sleep(2)

        text_mail = CHROME_DRIVER.find_element_by_class_name('letter__body')
        dict_for_mail['text_mail'] = ''.join(text_mail.text.replace('\u200c', '').replace('\n', ' '))

        contact = CHROME_DRIVER.find_element_by_class_name('letter-contact')
        dict_for_mail['contact_mail'] = contact.text

        date_ = CHROME_DRIVER.find_element_by_class_name('letter__date')
        dict_for_mail['date'] = date_.text

        subject = CHROME_DRIVER.find_element_by_class_name('thread__subject')
        dict_for_mail['subject'] = subject.text

        LIST_MAIL.append(dict_for_mail)
        CHROME_DRIVER.back()

    CHROME_DRIVER.close()

    data_base = client[db_name]

    insert_db(data_base, collection_name, LIST_MAIL)

except ConnectionFailure:
    print(u'Сервер MongoDB не доступен')

except OperationFailure:
    print(u'некорректное имя пользователя или пароль')
