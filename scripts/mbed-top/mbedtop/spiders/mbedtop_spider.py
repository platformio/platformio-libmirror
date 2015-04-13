import scrapy

from mbedtop.items import MbedItem

class MbedTopSpider(scrapy.Spider):
    name = "mbedtop"
    allowed_domains = ["developer.mbed.org"]
    start_urls = [
        "https://developer.mbed.org/search/?q=&selected_facets=obj_type_exact%3ACode+Repository&repo_type=Library&order_by=-import_count"
    ]
    top_max = 120
    top_cnt = 0

    def parse(self, response):
        # somehow, selecting div[@class="contentitem"] does not work; so:
        libraries = response.xpath('.//*[@id="mbed-content"]//div/div[2]/div[2]/div[1]/b/a/@href').extract()
        print "found libraries: ", libraries

        self.top_cnt = self.top_cnt + len(libraries)

        if self.top_cnt < self.top_max:
            # Request next page of results
            baseurl = response.url
            if 'baseurl' in response.meta: baseurl = response.meta['baseurl']
            pagenum = 1
            if 'pagenum' in response.meta: pagenum = response.meta['pagenum']
            nextpage = pagenum + 1
            request = scrapy.Request(baseurl+('&page=%d' % nextpage))
            request.meta['pagenum'] = nextpage
            request.meta['baseurl'] = baseurl
            yield request
