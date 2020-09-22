import scrapy
from scrapy.http import HtmlResponse
from items import JobparserItem


class HhruSpider(scrapy.Spider):
    name = 'hhru'
    allowed_domains = ['hh.ru']
    start_urls = ['https://hh.ru/search/vacancy?clusters=true&enable_snippets=true&text=python&L_save_area=true&area=1202&from=cluster_area&showClusters=true']

    def parse(self, response: HtmlResponse):
        vacancy_links = response.css("div.vacancy-serp-item__row_header a.bloko-link::attr(href)").extract()
        for link in vacancy_links:
            yield response.follow(link, callback=self.vacancy_parse)
        next_page = response.css("a.HH-Pager-Controls-Next::attr(href)").extract_first()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def vacancy_parse(self, response: HtmlResponse):
        name = response.xpath("//h1/text()").extract()
        salary = response.xpath("//p[@class='vacancy-salary']//text()").extract()
        link_vacancy = response.url
        yield JobparserItem(name=name, salary=salary, link_vacancy=link_vacancy)
