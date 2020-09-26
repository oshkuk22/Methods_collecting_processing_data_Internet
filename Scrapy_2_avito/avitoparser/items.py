# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.loader.processors import MapCompose


def str_to_int(value):
    if value:
        return int(value)


def description_(element):
    if element:
        return element.replace('\n', '').replace('  ', '')


class AvitoparserItem(scrapy.Item):
    # define the fields for your item here like:
    name = scrapy.Field()
    link_product = scrapy.Field()
    price = scrapy.Field(input_processor=MapCompose(str_to_int))
    currency = scrapy.Field()
    characteristics = scrapy.Field()
    characteristics_value = scrapy.Field(input_processor=MapCompose(description_))
    photos = scrapy.Field()
