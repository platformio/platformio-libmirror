import scrapy
from mbedtop.items import MbedLibItem, MbedLibLoader

from mbedtop.support import *

class MbedTopSpider(scrapy.Spider):
    name = "mbedtop"
    # allowed_domains = ["os.mbed.com"]
    allowed_domains = ["os.mbed.com"]
    # start_urls = [ "https://os.mbed.com/search/?q=&selected_facets=obj_type_exact%3ACode+Repository&repo_type=Library&order_by=-import_count" ]
    #start_urls = [ 'https://os.mbed.com/search/?type=&q=TMP102' ]
    start_urls = ["https://os.mbed.com/code/all/?sort=imports"]
    seen_urls = []
    lib_tags = {}   # will contain dict with "%NAME%" : [ %TAGS% ]

    top_max = 1000
    top_cnt = 0

    def parse(self, response):
        # libraries = response.xpath('.//*[@id="mbed-content"]//div/div[2]/div[2]/div[1]/b/a/@href').extract()
        libraries = response.xpath('.//*[@class="inline Library"]//a/@href').extract()
        print("found libraries: ", libraries)

        for url in libraries:
            if self.top_cnt < self.top_max:
                if url[0] == '/': url = 'https://os.mbed.com'+url
                if not url in self.seen_urls:
                    if not is_mbed_core_library(url=url):
                        self.top_cnt = self.top_cnt + 1
                    scrapy_requests = scrapy.Request(url,callback=self.parse_project)
                    scrapy_requests.meta['keywords'] = response.xpath('.//*[@class="inline Library"]/../../../a/text()').extract()
                    yield scrapy_requests

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
        # self.seen_urls.append(response.url)

        l = MbedLibLoader(item=MbedLibItem(), response=response)
        l.add_xpath('repo_type', './/*[@class="three columns sidebar "]//div[2]/table/tr[1]/td/text()[2]')
        l.add_xpath('owner', './/*[@class="code-header"]//a[1]/text()[2]')
        l.add_xpath('ownerurl', './/*[@class="code-header"]//a[1]/@href')
        l.add_xpath('name', './/*[@class="code-header"]//a[2]/text()[2]')
        l.add_xpath('repository', './/*[@class="code-header"]//a[2]/@href')
        l.add_xpath('description', './/*[@id="mbed-content"]/p[1]/text()')
        l.add_value('frameworks', 'mbed')
        l.add_value('platforms', mbed_platforms())
        l.add_xpath('components', './/*[@class="three columns sidebar "]//div[4]/a/@href')
        l.add_value('keywords',response.request.meta['keywords'])
        item = l.load_item()
        
        request = scrapy.Request(response.url+"dependencies",callback=self.parse_dependencies)
        request.meta['libpage'] = response.url
        request.meta['item'] = item
        return request

    def parse_dependencies(self, response):
        item = response.meta['item']
        
        # deplist = response.xpath('.//*[@id="mbed-content"]//div/div[2]/div[2]/div[1]/b/a/@href').extract()
        deplist = response.xpath('.//*[@id="mbed-content"]//div[2]/div[2]/div[2]/div/b/a/@href').extract()

        if len(deplist):
            print("****** dependencies for", item['name'], "are:",deplist)
            for url in deplist:
                if (url != "/") and (url[0] == '/') : url = 'https://os.mbed.com'+url
                if ("https://" in url and "components" not in url):# and not (url in self.seen_urls):
                    print (">>>>>>>>>>> follow dependency",url)
                    yield scrapy.Request(url,callback=self.parse_project,dont_filter=True)

            deps = []
            for url in deplist:
                url.replace("https://os.mbed.com/","")
                urllist = url.split('/') 
                print( "---- dependency urllist is len",len(urllist),": ",urllist)
                if (len(urllist) > 4) and not is_mbed_core_library(owner=urllist[2],name=urllist[4]):
                    deps_owner_nickname = urllist[2]
                    if(deps_owner_nickname!="components"):
                        owner_request = scrapy.Request('https://os.mbed.com/users/'+deps_owner_nickname, callback = self.parse_owner,dont_filter=True)
                        owner_request.meta['item'] = item
                        owner_request.meta['url'] = 'https://os.mbed.com/users/'+deps_owner_nickname
                        deps.append({ 'name' : urllist[4], 'frameworks' : 'mbed','url':"https://os.mbed.com" + url, 'authors':[{"url":'https://os.mbed.com/users/'+urllist[2]}] })
                        yield owner_request
            if len(deps)>0: item['dependencies'] = deps
            print("dependencies is ",deps)
        request = scrapy.Request(response.meta['libpage']+"dependents",callback=self.parse_examples)
        request.meta['libpage'] = response.meta['libpage']
        request.meta['item'] = item
        yield request

    def parse_examples(self, response):
        item = response.meta['item']
        examples = response.xpath('.//*[@id="mbed-content"]//div/div[2]/div[2]/div[1]/b/a/@href').extract()
        if len(examples): item['examples'] = examples

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
        url = "https://os.mbed.com"+item['ownerurl']+"code/?q="+item['name']

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
                print( "+++ Found keywords for", name, ": ", tags)
                self.log('Storing keywords for '+name[0])

        if item['name'] in self.lib_tags:
            item['keywords'] = self.lib_tags[item['name']]

        if len(next):
            print (">>> Next is",next)
            url = "https://os.mbed.com"+item['ownerurl']+"code/"+next[0]

            request = scrapy.Request(url,callback=self.parse_tags)
            request.meta['libpage'] = response.meta['libpage']
            request.meta['item'] = item
            return request

        return item

    def parse_owner(self, response):
        # self.seen_urls.append(response.url)
        item = response.meta['item']
        url = response.meta['url']
        owner = response.xpath('.//*[@id="mbed-content"]//div/div/div/div[2]/h3/text()').extract()

        print("|||||||||||||",item)
        print("||||||||||||||||")
        for i in range(len(item['dependencies'])):
            # if isinstance(resource, str):
            item['dependencies'][i]['authors'] = [owner[0]]
            item['dependencies'][i].pop('url', None)
            # if url == item['dependencies'][i]['authors']['url']:
                # item['dependencies'][i]['authors'].update({'name':owner[0]})
        return item
