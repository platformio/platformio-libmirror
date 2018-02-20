import scrapy
#from scrapy.contrib.loader import ItemLoader
from mbedtop.items import MbedLibItem, MbedLibLoader
#from mbedtop.pipelines import RepoPostProc

class MbedLibSpider(scrapy.Spider):
    name = "mbedlib"
    allowed_domains = ["developer.mbed.org"]
    start_urls = [
        #"http://developer.mbed.org/users/simon/code/TextLCD",
        #"http://developer.mbed.org/users/simon/code/TextLCD_HelloWorld/",
        #"http://developer.mbed.org/users/mbed_official/code/mbed/",
        "http://developer.mbed.org/users/mbed_official/code/EthernetInterface/"
    ]
    seen_urls = []

    # parse the library page
    def parse(self, response):
        self.seen_urls.append(response.url)

        l = MbedLibLoader(item=MbedLibItem(), response=response)
        l.add_xpath('repo_type', '/html/body/div[4]/div[2]/div[2]/table/tr[1]/td/text()[2]')
        l.add_xpath('owner', '/html/body/div[4]/div[1]/div/a[1]/text()[2]')
        l.add_xpath('name', '/html/body/div[4]/div[1]/div/a[2]/text()[2]')
        l.add_xpath('repository', '/html/body/div[4]/div[1]/div/a[2]/@href')
        l.add_xpath('description', './/*[@id="mbed-content"]/p[1]/text()') # may need some cleaning up \n
        l.add_value('frameworks', 'mbed')
        l.add_value('platforms', ['freescalekinetis', 'nordicnrf51', 'nxplpc', 'ststm32', 'teensy'])
        l.add_xpath('components', '/html/body/div[4]/div[2]/div[3]//a/@href')
        item = l.load_item()

        request = scrapy.Request(response.url+"dependencies",callback=self.parse_dependencies)
        request.meta['libpage'] = response.url
        request.meta['item'] = item
        return request

    def parse_dependencies(self, response):
        item = response.meta['item']
        l = MbedLibLoader(item=item, response=response)
        l.add_xpath('dependencies', './/*[@id="mbed-content"]//div/div[2]/div[2]/div[1]/b/a/@href')
        item = l.load_item()
        #TODO: generate requests for all dependents; ideally emit them before proceeding with examples
        if 'dependencies' in item:
            for url in item['dependencies']: 
                if url[0] == '/': url = 'http://developer.mbed.org'+url
                if not url in self.seen_urls:
                    yield scrapy.Request(url,callback=self.parse)

        request = scrapy.Request(response.meta['libpage']+"dependents",callback=self.parse_examples)
        request.meta['libpage'] = response.meta['libpage']
        request.meta['item'] = item
        yield request

    def parse_examples(self, response):
        item = response.meta['item']
        l = MbedLibLoader(item=item, response=response)
        l.add_xpath('examples', './/*[@id="mbed-content"]//div/div[2]/div[2]/div[1]/b/a/@href')
        item = l.load_item()
        return item

        # we could also add a search for this specific library to fill in keywords from tags:
        #request = scrapy.Request(response.meta['libpage']+"",callback=self.parse_tags)
        #request.meta['libpage'] = response.meta['libpage']
        #request.meta['item'] = item
        #return request

    def parse_tags(self, response):
        item = response.meta['item']
        l = MbedLibLoader(item=item, response=response)
        #TODO: formulate xpath to extract all tags (keywords)
        l.add_xpath('keywords', '/html/body/div[4]/div[1]/div/a[2]/@href')
        item = l.load_item()
        return item

