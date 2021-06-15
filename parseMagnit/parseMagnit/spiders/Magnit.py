import scrapy
import datetime
import time
import json
import re


class MagnitSpider(scrapy.Spider):
    name = 'Magnit'
    allowed_domains = ['magnitcosmetic.ru']
    start_urls = ['https://magnitcosmetic.ru/catalog/kosmetika/brite_i_epilyatsiya/',
                  'https://magnitcosmetic.ru/catalog/kosmetika/detskaya_kosmetika_i_ukhod/']
    price_load_url = 'https://magnitcosmetic.ru/local/ajax/load_remains/catalog_load_remains.php'

    def start_requests(self):
        for category_url in self.start_urls:
            yield scrapy.Request(category_url, callback=self.parse)

    def parse(self, response):
        pageCount = int(response.xpath("//div[@class='pageCount']/text()").extract_first())
        curPage = int(response.xpath("//div[@class = 'curPage']/text()").extract_first())

        for href in response.xpath("//a[contains(@class, 'product__link')]/@href").extract():
            url_page = self.formUrl(href)
            yield scrapy.Request(url_page, callback=self.parsePage)

        quotes_base_url = response.urljoin('?PAGEN_1=%s')
        if curPage != pageCount:
            next_page = curPage + 1
            yield scrapy.Request(quotes_base_url % next_page, callback=self.parse)

    def parsePage(self, response):

        result = {"timestamp": datetime.datetime.now().timestamp()}

        result |= {"RPC": response.url.split('/')[-2]}

        result |= {
            "title": MagnitSpider.clearStr(response.xpath("//h1[@class = 'action-card__name']/text()").extract_first())}

        result |= {"marketing tags": response.xpath("//span[@class = 'event__product-title']/text()").extract()}

        result |= {
            "brand": response.xpath("//td[@class = 'action-card__cell']/text()").extract()[1].strip('\n\t').strip()}

        section = response.xpath("//a[@class = 'breadcrumbs__link']/text()").extract()
        for i in range(len(section)):
            section[i] = MagnitSpider.clearStr(section[i])
        result |= {"section": section}

        # headers = {
        #     "X-Requested-With": "XMLHttpRequest",
        #     "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        #     "Refer": response.url
        # }
        # products_code = response.xpath("//script[contains(text(), 'PRODUCT_XML_CODE')]/text()").extract_first()
        # products_code = json.loads(re.search('{.*', products_code)[0])
        # body = {
        #     "SHOP_XML_CODE": response.xpath("//input[@class = 'js-shop__xml-code']/@value").extract_first(),
        #     "PRODUCTS": products_code,
        #     "JUST_ONE": "Y",
        #     "enigma": response.xpath("//input[@class = 'js-remains__detail']/@value").extract_first(),
        #     "type": 'detail'
        # }

        assets = {"main_image": self.formUrl(response.xpath("//img[@class = 'product__image']/@src").extract_first()),
                  "set_images": [],
                  "view360": [],
                  "video": []}
        result |= {"assets": assets}

        metadata = {"description": response.xpath("//div[@class = 'action-card__text']/text()").extract_first()}
        item_list = response.xpath("//td[@class = 'action-card__cell']/text()").extract()[2:]
        for i in range(0, len(item_list), 2):
            metadata |= {MagnitSpider.clearStr(item_list[i])[:-1]: MagnitSpider.clearStr(item_list[i + 1])}
        result |= metadata

        result |= {"variant": 1}

        # yield scrapy.Request(self.price_load_url, callback=self.parsePrice, method='POST', headers=headers,
        #                      body=json.dumps(body).encode(), meta={"result": result})
        yield result

    # def parsePrice(self, response):
    #     result = response.meta["result"]
    #     price = json.loads(response.text)
    #     yield result

    def formUrl(self, url):
        return 'https://' + self.allowed_domains[0] + url

    @staticmethod
    def clearStr(str):
        return str.strip('\n\t').strip()
