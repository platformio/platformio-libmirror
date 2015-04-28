import scrapy
from mbedtop.items import MbedLibItem, MbedLibLoader

from mbedtop.support import *

class MbedTopSpider(scrapy.Spider):
    name = "mbedtop"
    allowed_domains = ["developer.mbed.org"]
    start_urls = [ "https://developer.mbed.org/search/?q=&selected_facets=obj_type_exact%3ACode+Repository&repo_type=Library&order_by=-import_count" ]
    #start_urls = [ 'https://developer.mbed.org/search/?type=&q=TMP102' ]
    seen_urls = []
    lib_tags = {}   # will contain dict with "%NAME%" : [ %TAGS% ]

    top_max = 100
    top_cnt = 0

    def parse(self, response):
        libraries = response.xpath('.//*[@id="mbed-content"]//div/div[2]/div[2]/div[1]/b/a/@href').extract()
        print "found libraries: ", libraries

        for url in libraries:
            if self.top_cnt < self.top_max:
                if url[0] == '/': url = 'https://developer.mbed.org'+url
                if not url in self.seen_urls:
                    if not is_mbed_core_library(url=url):
                        self.top_cnt = self.top_cnt + 1
                    yield scrapy.Request(url,callback=self.parse_project)

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

    # parse the library page
    def parse_project(self, response):
        self.seen_urls.append(response.url)

        l = MbedLibLoader(item=MbedLibItem(), response=response)
        l.add_xpath('repo_type', '/html/body/div[4]/div[2]/div[2]/table/tr[1]/td/text()[2]')
        l.add_xpath('owner', '/html/body/div[4]/div[1]/div/a[1]/text()[2]')
        l.add_xpath('ownerurl', '/html/body/div[4]/div[1]/div/a[1]/@href')
        l.add_xpath('name', '/html/body/div[4]/div[1]/div/a[2]/text()[2]')
        l.add_xpath('repository', '/html/body/div[4]/div[1]/div/a[2]/@href')
        l.add_xpath('description', './/*[@id="mbed-content"]/p[1]/text()')
        l.add_value('frameworks', 'mbed')
        l.add_value('platforms', mbed_platforms())
        l.add_xpath('components', '/html/body/div[4]/div[2]/div[3]//a/@href')
        item = l.load_item()

        request = scrapy.Request(response.url+"dependencies",callback=self.parse_dependencies)
        request.meta['libpage'] = response.url
        request.meta['item'] = item
        return request

    def parse_dependencies(self, response):
        item = response.meta['item']
        
        deplist = response.xpath('.//*[@id="mbed-content"]//div/div[2]/div[2]/div[1]/b/a/@href').extract()

        if len(deplist):
            print "****** dependencies for",item['name'],"are:",deplist
            for url in deplist:
                if (url != "/") and (url[0] == '/') : url = 'https://developer.mbed.org'+url
                if ("https://" in url) and not (url in self.seen_urls):
                    print ">>>>>>>>>>> follow dependency",url
                    yield scrapy.Request(url,callback=self.parse_project)

            deps = []
            for url in deplist:
                url.replace("https://developer.mbed.org/","")
                urllist = url.split('/') 
                #print "---- dependency urllist is len",len(urllist),": ",urllist
		if (len(urllist) > 4) and not is_mbed_core_library(owner=urllist[2],name=urllist[4]):
                    deps.append({ 'name' : urllist[4], 'frameworks' : 'mbed' })

            if len(deps): item['dependencies'] = deps

        request = scrapy.Request(response.meta['libpage']+"dependents",callback=self.parse_examples)
        request.meta['libpage'] = response.meta['libpage']
        request.meta['item'] = item
        yield request

    def parse_examples(self, response):
        item = response.meta['item']
        l = MbedLibLoader(item=item, response=response)
        l.add_xpath('examples', './/*[@id="mbed-content"]//div/div[2]/div[2]/div[1]/b/a/@href')
        item = l.load_item()

        # if we already know keywords, we can used cached results:
        if 0 and (item['name'] in self.lib_tags):
            item['keywords'] = self.lib_tags[item['name']]
            self.log('Found keywords for '+item['name']+' in lib_tags')
            return item

        # otherwise, proceed with keyword extraction:
        if not 'ownerurl' in item:
            self.log('Found no keywords for '+item['name']+' in lib_tags and no ownerurl')
            return item

        # note that duplicate requests will be dropped, so make sure to use unique url!
        url = "https://developer.mbed.org"+item['ownerurl']+"code/?q="+item['name']

        request = scrapy.Request(url,callback=self.parse_tags)
        request.meta['libpage'] = response.meta['libpage']
        request.meta['item'] = item
        return request

    def parse_tags(self, response):
        item = response.meta['item']

        next = response.xpath(".//*[@class='paginate-next']/a/@href").extract()

        for elem in response.xpath('.//*[@id="mbed-content"]/div'):
            name = elem.xpath('div[2]/div/div[1]/b/a/text()').extract()
            tags = elem.xpath('div[2]/div/div[2]/a/text()').extract()

            if (len(name) > 0) and (len(tags) > 0):
                self.lib_tags[name[0]] = tags
                print "+++ Found keywords for", name, ": ", tags
                self.log('Storing keywords for '+name[0])

        if item['name'] in self.lib_tags:
            item['keywords'] = self.lib_tags[item['name']]

        if len(next):
            print ">>> Next is",next
            url = "https://developer.mbed.org"+item['ownerurl']+"code/"+next[0]

            request = scrapy.Request(url,callback=self.parse_tags)
            request.meta['libpage'] = response.meta['libpage']
            request.meta['item'] = item
            return request

        return item
