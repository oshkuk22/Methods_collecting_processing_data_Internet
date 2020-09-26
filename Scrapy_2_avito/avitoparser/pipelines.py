# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import hashlib

import scrapy
from scrapy.pipelines.images import ImagesPipeline
from pymongo import MongoClient
import pymongo.errors
from scrapy.utils.python import to_bytes


class AvitoparserPipeline:
    def __init__(self):
        host_name = '192.168.1.35'
        port_name = 61290
        db_name = 'leroy'
        db_user = 'leroy'
        db_pwd = 'leroy!'
        try:
            client = MongoClient(host_name, port_name,
                                 username=db_user,
                                 password=db_pwd,
                                 authSource=db_name,
                                 authMechanism="SCRAM-SHA-1",
                                 connect=True)

            self.data_base = client[db_name].command("ismaster")
            self.data_base = client[db_name]

        except pymongo.errors.ConnectionFailure:
            print(u'Сервер MongoDB не доступен')

        except pymongo.errors.OperationFailure:
            print(u'некорректное имя пользователя или пароль')

    def process_item(self, item, spider):
        if spider:
            info_product = {'name': item['name'][0], 'link_product': item['link_product'][0],
                            'price': item['price'][0], 'currency': item['currency'][0],
                            'characteristics': dict(zip(item['characteristics'], item['characteristics_value'])),
                            'photos': item['photos']}
            self.data_base[spider.name].update_one(info_product, {'$set': info_product}, upsert=True)
        return item


class PhotosProductPipeLine(ImagesPipeline):
    def get_media_requests(self, item, info):
        if item['photos']:
            for img in item['photos']:
                try:
                    yield scrapy.Request(img, meta=item)
                except Exception as e:
                    print(e)

    def file_path(self, request, response=None, info=None):
        source_name = request.meta['link_product'][0].split('/')[2]
        path_name = request.meta['link_product'][0].split('/')[4]
        image_guid = hashlib.sha1(to_bytes(request.url)).hexdigest()
        return 'full/%s/%s/%s.jpg' % (source_name, path_name, image_guid)

    def item_completed(self, results, item, info):
        if results:
            item['photos'] = [elem_[1] for elem_ in results if elem_[0]]
        return item
