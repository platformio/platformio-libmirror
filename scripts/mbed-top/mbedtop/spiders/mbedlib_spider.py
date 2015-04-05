import scrapy
#from scrapy.contrib.loader import ItemLoader
from mbedtop.items import MbedLibItem, MbedLibLoader

class MbedLibSpider(scrapy.Spider):
    name = "mbedlib"
    allowed_domains = ["developer.mbed.org"]
    start_urls = [
        "http://developer.mbed.org/users/simon/code/TextLCD",
        "http://developer.mbed.org/users/simon/code/TextLCD_HelloWorld/",
        "http://developer.mbed.org/users/mbed_official/code/mbed/"
    ]

    def parse(self, response):
        l = MbedLibLoader(item=MbedLibItem(), response=response)
        l.add_xpath('repo_type', '/html/body/div[4]/div[2]/div[2]/table/tr[1]/td/text()[2]')
        l.add_xpath('owner', '/html/body/div[4]/div[1]/div/a[1]/text()[2]')
        l.add_xpath('name', '/html/body/div[4]/div[1]/div/a[2]/text()[2]')
        l.add_xpath('repository', '/html/body/div[4]/div[1]/div/a[2]/@href')
        l.add_xpath('description', './/*[@id="mbed-content"]/p[1]/text()') # may need some cleaning up \n
        #item['frameworks']  = 'mbed'
        #item['platforms']   = ['freescalekinetis', 'nordicnrf51', 'nxplpc', 'ststm32']
        l.add_xpath('components', '/html/body/div[4]/div[2]/div[3]//a/@href')
        l.add_xpath('deplist1', './/*[@id="mbed-content"]/p[2]/b/a/text()')
        l.add_xpath('deplist1', './/*[@id="mbed-content"]/p[2]/a/@href')
        l.add_xpath('deplist2', './/*[@id="mbed-content"]/p[3]/b/a/@href')
        l.add_xpath('deplist2', './/*[@id="mbed-content"]/p[3]/a/@href')
        #l.add
        l.add_value('examples', [''])
        l.add_value('dependencies', [''])
        return l.load_item()
