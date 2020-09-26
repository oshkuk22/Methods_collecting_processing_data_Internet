from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings

from spiders.leroy import LeroySpider
import settings

if __name__ == '__main__':
    crawler_settings = Settings()
    crawler_settings.setmodule(settings)

    process = CrawlerProcess(settings=crawler_settings)

    process.crawl(LeroySpider, for_search=['barnaul', 'морилка'])

    process.start()
