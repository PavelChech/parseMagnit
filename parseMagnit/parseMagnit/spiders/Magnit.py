import scrapy
import datetime

class MagnitSpider(scrapy.Spider):
    name = 'Magnit'
    allowed_domains = ['magnitcosmetic.ru']
    start_urls = ['https://magnitcosmetic.ru/catalog/kosmetika/brite_i_epilyatsiya/']

    def parse(self, response):
        pageCount = int(response.xpath("//div[@class='pageCount']/text()").extract_first())
        curPage = int(response.xpath("//div[@class = 'curPage']/text()").extract_first())
        # print("----------------------Parse--------------------------")
        # print(curPage, pageCount)

        for href in response.xpath("//a[contains(@class, 'product__link')]/@href").extract():
            url_page = 'https://' + self.allowed_domains[0] + href
            # print(url_page)
            yield scrapy.Request(url_page, callback=self.parsePage)
        
        quotes_base_url = 'https://magnitcosmetic.ru/catalog/kosmetika/brite_i_epilyatsiya/?PAGEN_1=%s'
        if  curPage != pageCount: 
            next_page = curPage + 1
            yield scrapy.Request(quotes_base_url % next_page, callback=self.parse)
        

    def parsePage(self, response):
        timestamp = datetime.datetime.now().timestamp()
        # print("----------------------parsePage--------------------------")
        result = {
            "timestamp": timestamp,
            # "RPC": RPC,
            # "color": color,
            # "url": url,
            # "title" : title,
            # "marketing tags": marketing_tags,
            # "brand": brand,
            # "section": section,
            # "price data": {"current": current_price,
            #               "original": original_price,
            #               "sale_tag": sale_tag},
            # "stock":{"in stock": in_stock,
            #          "count": 0},
            # "assets": {"main image": main_image,
            #            "set images": set_images,
            #            "view360": view,
            #            "video": video},
            # "metadata": {"description": description,
            #              "metadata": metadata},
            # "variants": variants
        }

        yield result