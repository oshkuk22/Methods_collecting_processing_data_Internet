import scrapy
from scrapy.http import HtmlResponse
from items import AvitoparserItem
from scrapy.loader import ItemLoader


class LeroySpider(scrapy.Spider):
    name = 'leroy'
    allowed_domains = ['leroymerlin.ru']

    def __init__(self, for_search):
        self.start_urls = [f'https://{for_search[0]}.leroymerlin.ru/search/?q={for_search[1]}']

    def parse(self, response: HtmlResponse):
        link_product = response.xpath('//a[@slot="name"]')
        for link_ in link_product:
            yield response.follow(link_, callback=self.parse_link_product)
        next_page = response.xpath('//a[@data-js-pagination-next-btn]/@href').extract_first()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

    @staticmethod
    def parse_link_product(response: HtmlResponse):
        loader = ItemLoader(item=AvitoparserItem(), response=response)
        loader.add_xpath('name', '//h1/text()')
        loader.add_xpath('price', '//uc-pdp-price-view[@slot="primary-price"]/span[@slot="price"]/text()')
        loader.add_xpath('currency', '//uc-pdp-price-view[@slot="primary-price"]/span[@slot="currency"]/text()')
        loader.add_xpath('characteristics', '//section[@id="nav-characteristics"]//dt/text()')
        loader.add_xpath('characteristics_value', '//section[@id="nav-characteristics"]//dd/text()')
        loader.add_xpath('photos', '//picture//source[@data-origin]/@data-origin')
        loader.add_value('link_product', response.url)
        yield loader.load_item()

