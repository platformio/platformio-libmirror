import scrapy
import csv
from mbedtop.items import MbedLibItem, MbedLibLoader

from mbedtop.support import *


class MbedTopSpider(scrapy.Spider):
    name = "mbedtop"
    allowed_domains = ["os.mbed.com"]
    start_urls = ["https://os.mbed.com/code/all/?sort=imports"]
    seen_urls = []
    lib_tags = {}  # will contain dict with "%NAME%" : [ %TAGS% ]

    top_max = 4000
    top_cnt = 0

    def parse(self, response):
        libraries = response.xpath(
            './/*[@class="inline Library"]//a/@href').extract()
        print("found libraries: ", libraries)
        for url in libraries:
            if self.top_cnt < self.top_max:
                if url[0] == '/':
                    url = 'https://os.mbed.com' + url
                if url not in self.seen_urls:
                    if not is_mbed_core_library(url=url):
                        self.top_cnt = self.top_cnt + 1
                    scrapy_requests = scrapy.Request(
                        url, callback=self.parse_project, dont_filter=True)
                    scrapy_requests.meta['keywords'] = response.xpath(
                        './/*[@class="inline Library"]/../../../a/text()'
                    ).extract()
                    yield scrapy_requests

        if self.top_cnt < self.top_max:
            # Request next page of results
            baseurl = response.url
            if 'baseurl' in response.meta:
                baseurl = response.meta['baseurl']
            pagenum = 1
            if 'pagenum' in response.meta:
                pagenum = response.meta['pagenum']
            nextpage = pagenum + 1
            request = scrapy.Request(
                baseurl + ('&page=%d' % nextpage), dont_filter=True)
            request.meta['pagenum'] = nextpage
            request.meta['baseurl'] = baseurl
            yield request

    # parse the library page
    def parse_project(self, response):
        # self.seen_urls.append(response.url)
        l = MbedLibLoader(item=MbedLibItem(), response=response)
        l.add_xpath(
            'repo_type',
            './/*[@class="three columns sidebar "]//div[2]/table/tr[1]/td/text()[2]'
        )
        l.add_xpath('owner', './/*[@class="code-header"]//a[1]/text()[2]')
        l.add_xpath('ownerurl', './/*[@class="code-header"]//a[1]/@href')
        l.add_xpath('name', './/*[@class="code-header"]//a[2]/text()[2]')
        l.add_xpath('repository', './/*[@class="code-header"]//a[2]/@href')
        l.add_xpath('description', './/*[@id="mbed-content"]/p[1]/text()')
        l.add_value('frameworks', 'mbed')
        l.add_value('platforms', mbed_platforms())
        l.add_xpath('fork', './/*[@class="authortext"]/../a/text()')
        # l.add_xpath('commits', './/*[@id="container"]/div[2]/h2/text()')
        l.add_xpath('commits', './/*[@class="fa icon_commits"]//../text()')
        l.add_xpath('dependents',
                    './/*[@class="fa icon_repo_depens"]//../text()')
        l.add_xpath('components',
                    './/*[@class="three columns sidebar "]//div[4]/a/@href')
        l.add_xpath('imports', './/*[@class="fa icon_imports"]//../text()')
        l.add_value('keywords', response.request.meta['keywords'])
        item = l.load_item()
        # item['imports']  = get_import_number(item['imports'])

        if is_fork(item):
            return

        if int(item['commits']) < 1:
            return
            
        with open('libs.csv', 'a', newline='') as csv_file:
            writer =csv.writer(csv_file, delimiter=';')
            writer.writerow([
                make_mbed_url(item['repository']),
                is_fork(item),
                int(item['imports']),
                int(item['dependents'])
                ])

        # if is_fork(item) and int(item['dependents']) < 5:
        #     with open("fork_dependents_less5.txt", "a") as myfile:
        #         myfile.write("\nitem %s/%s/%s" % (item['owner'], item['name'],
        #                                           item['repository']))
        #     return
        if int(item['imports']) < 5:
            with open("imports_less10.txt", "a") as myfile:
                myfile.write("\nitem %s/%s/%s" % (item['owner'], item['name'],
                                                  item['repository']))
            return

        if has_non_ascii_char(item['ownerurl']) or has_non_ascii_char(
                item['repository']):
            with open("non_ASCII.txt", "a") as myfile:
                myfile.write("\nitem %s/%s/%s" % (item['owner'], item['name'],
                                                  item['repository']))
            return

        if not ('description' in item):
            item['description'] = item['name']
        if not ('keywords' in item):
            item['keywords'] = item['name']
        request = scrapy.Request(
            response.url + "dependencies",
            callback=self.parse_dependencies,
            dont_filter=True)
        request.meta['libpage'] = response.url
        request.meta['item'] = item
        return request

    def parse_dependencies(self, response):
        item = response.meta['item']
        deplist = response.xpath(
            './/*[@id="mbed-content"]//div[2]/div[2]/div[2]/div/b/a/@href'
        ).extract()

        if len(deplist):
            print("****** dependencies for", item['name'], "are:", deplist)
            for url in deplist:
                if (url != "/") and (url[0] == '/'):
                    url = 'https://os.mbed.com' + url
                if ("https://" in url and "components" not in url):
                    print(">>>>>>>>>>> follow dependency", url)
                    yield scrapy.Request(
                        url, callback=self.parse_project, dont_filter=True)

            deps = []
            for url in deplist:
                url.replace("https://os.mbed.com/", "")
                urllist = url.split('/')
                print("---- dependency urllist is len", len(urllist), ": ",
                      urllist)
                if (len(urllist) > 4) and not is_mbed_core_library(
                        owner=urllist[2], name=urllist[4]):
                    deps_owner_nickname = urllist[2]
                    if (deps_owner_nickname != "components"):
                        owner_request = scrapy.Request(
                            'https://os.mbed.com/' + urllist[1] + '/' +
                            deps_owner_nickname,
                            callback=self.parse_owner,
                            dont_filter=True)
                        owner_request.meta['item'] = item
                        owner_request.meta[
                            'url'] = 'https://os.mbed.com/' + urllist[1] + '/' + deps_owner_nickname
                        deps.append({
                            'name':
                            urllist[4],
                            'frameworks':
                            'mbed',
                            'url':
                            "https://os.mbed.com" + url,
                            'authors': [{
                                "url":
                                'https://os.mbed.com/' + urllist[1] + '/' +
                                urllist[2]
                            }]
                        })
                        yield owner_request
            if len(deps) > 0:
                item['dependencies'] = deps
            print("dependencies is ", deps)
        request = scrapy.Request(
            response.meta['libpage'] + "dependents",
            callback=self.parse_examples,
            dont_filter=True)
        request.meta['libpage'] = response.meta['libpage']
        request.meta['item'] = item
        yield request

    def parse_examples(self, response):
        item = response.meta['item']
        examples = response.xpath(
            './/*[@id="mbed-content"]//div/div[2]/div[2]/div[1]/b/a/@href'
        ).extract()
        if len(examples):
            item['examples'] = examples

        # if we already know keywords, we can used cached results:
        if 0 and (item['name'] in self.lib_tags):
            item['keywords'] = self.lib_tags[item['name']]
            self.log('Found keywords for ' + item['name'] + ' in lib_tags')
            return item

        # otherwise, proceed with keyword extraction:
        if 'ownerurl' not in item:
            self.log('Found no keywords for ' + item['name'] +
                     ' in lib_tags and no ownerurl')
            return item

        # note that duplicate requests will be dropped, so make sure to use unique url!
        url = "https://os.mbed.com" + item['ownerurl'] + "code/?q=" + item['name']

        request = scrapy.Request(
            url, callback=self.parse_tags, dont_filter=True)
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
                print("+++ Found keywords for", name, ": ", tags)
                self.log('Storing keywords for ' + name[0])

        if item['name'] in self.lib_tags:
            item['keywords'] = self.lib_tags[item['name']]

        if len(next):
            print(">>> Next is", next)
            url = "https://os.mbed.com" + item['ownerurl'] + "code/" + next[0]

            request = scrapy.Request(
                url, callback=self.parse_tags, dont_filter=True)
            request.meta['libpage'] = response.meta['libpage']
            request.meta['item'] = item
            return request

        return item

    def parse_owner(self, response):

        item = response.meta['item']
        url = response.meta['url']
        urlsplit = url.split('/')
        owner = ''
        if 'users' in urlsplit:
            owner = response.xpath(
                './/*[@id="mbed-content"]//div/div/div/div[2]/h3/text()'
            ).extract()[0]
        if 'teams' in urlsplit:
            owner = response.xpath(
                './/*[@class="twelve columns profile"]//div/h3/a/text()[1]'
            ).extract()[0]
        for i in range(len(item['dependencies'])):
            item['dependencies'][i]['authors'] = [owner]
            item['dependencies'][i].pop('url', None)

        return item
