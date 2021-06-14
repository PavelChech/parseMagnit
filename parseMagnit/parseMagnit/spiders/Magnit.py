import scrapy
import datetime
import time
import json 


class MagnitSpider(scrapy.Spider):
    name = 'Magnit'
    allowed_domains = ['magnitcosmetic.ru']
    start_urls = ['https://magnitcosmetic.ru/catalog/kosmetika/brite_i_epilyatsiya/',
                'https://magnitcosmetic.ru/catalog/kosmetika/detskaya_kosmetika_i_ukhod/']


    def start_requests(self):
        for category_url in self.start_urls:
            yield scrapy.Request(category_url, callback=self.parse)


    def parse(self, response):
        pageCount = int(response.xpath("//div[@class='pageCount']/text()").extract_first())
        curPage = int(response.xpath("//div[@class = 'curPage']/text()").extract_first())

        for href in response.xpath("//a[contains(@class, 'product__link')]/@href").extract():
            url_page = 'https://' + self.allowed_domains[0] + href
            yield scrapy.Request(url_page, callback=self.parsePage)
        
        quotes_base_url = response.urljoin('?PAGEN_1=%s')
        if  curPage != pageCount: 
            next_page = curPage + 1
            yield scrapy.Request(quotes_base_url % next_page, callback=self.parse)
        

    def parsePage(self, response):
        
        result = {"timestamp": datetime.datetime.now().timestamp()}
        
        result |= {"RPC": response.url.split('/')[-2]}

        result |= {"title": MagnitSpider.clearStr(response.xpath("//h1[@class = 'action-card__name']/text()").extract_first())}

        result |= {"marketing tags": response.xpath("//span[@class = 'event__product-title']/text()").extract()}

        result |= {"brand": response.xpath("//td[@class = 'action-card__cell']/text()").extract()[1].strip('\n\t').strip()}

        section = response.xpath("//a[@class = 'breadcrumbs__link']/text()").extract()
        for i in range(len(section)):
            section[i] = MagnitSpider.clearStr(section[i])
        result |= {"section": section}

        assets = {"main_image": 'https://' + self.allowed_domains[0] + response.xpath("//img[@class = 'product__image']/@src").extract_first(),
                    "set_images": [],
                    "view360": [], 
                    "video": []}  
        result |= {"assets": assets}

        metadata = {"description": response.xpath("//div[@class = 'action-card__text']/text()").extract_first()}
        item_list = response.xpath("//td[@class = 'action-card__cell']/text()").extract()[2:]
        for i in range(0, len(item_list), 2):
            metadata |= {MagnitSpider.clearStr(item_list[i])[:-1]: MagnitSpider.clearStr(item_list[i+1])}
        result |= metadata

        result |= {"variant": 1}

        yield result

    # def parseEvent(self, response):
    #     pass

    @staticmethod
    def clearStr(str):
        return str.strip('\n\t').strip()