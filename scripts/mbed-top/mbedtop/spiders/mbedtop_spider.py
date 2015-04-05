import scrapy

from mbedtop.items import MbedItem

class MbedTopSpider(scrapy.Spider):
    name = "mbedtop"
    allowed_domains = ["developer.mbed.org"]
    start_urls = [
        "http://developer.mbed.org/search/?q=&selected_facets=obj_type_exact%3ACode+Repository&repo_type=Library&order_by=-import_count"
    ]

    def parse(self, response):
        # somehow, selecting div[@class="contentitem"] does not work; so:
        for sel in response.xpath('//div[@class="row"]/div[@class="nine columns main-content"]/div'):
            item = MbedItem()
            item['authors']     = sel.xpath('div[2]/div[2]/div[1]/a/text()').extract()
            item['name']        = sel.xpath('div[2]/div[2]/div[1]/b/a/text()').extract()
            item['repository']  = sel.xpath('div[2]/div[2]/div[1]/b/a/@href').extract()
            item['description'] = sel.xpath('div[2]/div[2]/div[2]/div/text()').extract() # may need some cleaning up \n
            item['frameworks']  = 'mbed'
            item['platforms']   = ['freescalekinetis', 'nordicnrf51', 'nxplpc', 'ststm32']
            item['keywords']    = sel.xpath('div[2]/div[2]/div[2]/a/text()').extract()
            yield item
