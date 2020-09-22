# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from pymongo import MongoClient
import pymongo.errors

class JobparserPipeline:
    def __init__(self):
        host_name = '192.168.1.35'
        port_name = 61290
        db_name = 'jobs_scrapy'
        db_user = 'scrapy'
        db_pwd = 'scrapy!'
        try:
            client = MongoClient(host_name, port_name,
                                 username=db_user,
                                 password=db_pwd,
                                 authSource=db_name,
                                 authMechanism="SCRAM-SHA-1",
                                 connect=True)

            self.data_base = client[db_name].command("ismaster")
            self.data_base= client[db_name]

        except pymongo.errors.ConnectionFailure:
            print(u'Сервер MongoDB не доступен')

        except pymongo.errors.OperationFailure:
            print(u'некорректное имя пользователя или пароль')

    def process_item(self, item, spider):
        if spider.name == 'hhru':
            info_vacancy = {'name_vacancy': item['name'][0], 'link_': item['link_vacancy'], 'source': 'hhru',
                            'salary': self.parsing_salary_hh(item['salary'])['salary']}
            self.data_base[spider.name].update_one(info_vacancy, {'$set': info_vacancy}, upsert=True)
        elif spider.name == 'superjob':
            info_vacancy = {'name_vacancy': item['name'][0], 'link_': item['link_vacancy'], 'source': 'superjob',
                            'salary': self.parsing_salary_superjob(item['salary'])['salary']}
            self.data_base[spider.name].update_one(info_vacancy, {'$set': info_vacancy}, upsert=True)
        return item

    @staticmethod
    def parsing_salary_hh(salary_):
        dict_salary = {}
        final_dict = {}
        if len(salary_) == 5:
           if salary_[0] == u'от ':
               dict_salary['minimum'] = salary_[1].replace('\xa0','')
               dict_salary['maximum'] = None
               dict_salary['currency'] = salary_[3]
               dict_salary['condition'] = salary_[4]
           elif salary_[0] == u'до ':
               dict_salary['minimum'] = None
               dict_salary['maximum'] = salary_[2].replace('\xa0','')
               dict_salary['currency'] = salary_[3]
               dict_salary['condition'] = salary_[4]
           final_dict['salary'] = dict_salary
        elif len(salary_) == 7:
            dict_salary['minimum'] = salary_[1].replace('\xa0','')
            dict_salary['maximum'] = salary_[3].replace('\xa0','')
            dict_salary['currency'] = salary_[5]
            dict_salary['condition'] = salary_[6]
            final_dict['salary'] = dict_salary
        else:
            final_dict['salary'] = salary_[0]

        return final_dict

    @staticmethod
    def parsing_salary_superjob(salary_):
        dict_salary = {}
        final_dict = {}
        if len(salary_) == 3:
            s_pars = salary_[2].split('\xa0')
            if salary_[0] == u'от':
                dict_salary['minimum'] = s_pars[0] + s_pars[1]
                dict_salary['maximum'] = None
                dict_salary['currency'] = s_pars[2]
            elif salary_[0] == u'до':
                dict_salary['minimum'] = None
                dict_salary['maximum'] = s_pars[0] + s_pars[1]
                dict_salary['currency'] = s_pars[2]
            else:
                dict_salary['minimum'] = salary_[0].replace('\xa0', '')
                dict_salary['maximum'] = salary_[0].replace('\xa0', '')
                dict_salary['currency'] = salary_[2]
            final_dict['salary'] = dict_salary
        elif len(salary_) == 7:
            dict_salary['minimum'] = salary_[0].replace('\xa0', '')
            dict_salary['maximum'] = salary_[4].replace('\xa0', '')
            dict_salary['currency'] = salary_[6]
            final_dict['salary'] = dict_salary
        else:
            final_dict['salary'] = salary_[0]

        return final_dict
