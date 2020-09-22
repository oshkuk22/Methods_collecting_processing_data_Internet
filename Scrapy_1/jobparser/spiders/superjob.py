import scrapy
from scrapy.http import HtmlResponse
from items import JobparserItem


class SuperjobSpider(scrapy.Spider):
    name = 'superjob'
    allowed_domains = ['superjob.ru']
    start_urls = ['https://russia.superjob.ru/vacancy/search/?keywords=python']

    def parse(self, response: HtmlResponse):
        vacancy_links = response.xpath("//a[contains(@class,'icMQ_ _6AfZ9')]/@href").extract()
        for link in vacancy_links:
            yield response.follow(link, callback=self.vacancy_parse)
        next_page = response.css("a.f-test-link-Dalshe::attr(href)").extract_first()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def vacancy_parse(self, response: HtmlResponse):
        name = response.xpath("//h1/text()").extract()
        salary = response.xpath("//span[@class='_3mfro _2Wp8I PlM3e _2JVkc']//text()").extract()
        link_vacancy = response.url
        yield JobparserItem(name=name, salary=salary, link_vacancy=link_vacancy)