# -*- coding: utf-8 -*-
import logging
import json
import hashlib
import codecs
import os
import scrapy
from mbedtop.items import MbedParserItem, MbedParserLoader

# logging.basicConfig()
# logger = logging.getLogger('mbedtop.spiders')
# logger.setLevel("WARNING")
#

class MbedTerrierSpider(scrapy.Spider):
    name = 'mbed_terrier'
    allowed_domains = ['os.mbed.com']
    start_urls = ['https://os.mbed.com/code/all/?sort=imports']
    # lib_page_max = 1000000
    # lib_page_cnt = 0
    stop = False
    current_page = 1
    total_libs = 0

    def make_mbed_url(self, url):
        if isinstance(url, str):
            return "https://os.mbed.com" + url
        return [self.make_mbed_url(link) for link in url[:10]]

    def has_non_ascii_char(self, value):
        return any(ord(c) > 128 for c in value)

    def is_mbed_core_library(self, url='', name='', owner=''):
        blacklist = [
            'FATFileSystem',
            'mbed',
            'mbed-rtos',
            'mbed-src',
            'mbed-rpc',
            'lwip',
            'lwip-eth',
            'lwip-sys',
            'EthernetInterface',
            'Socket',
            'spi',
            'FFT',
        ]
        if "https://" in url:
            url = self.strip_mbed_url(url).split('/')
            # owner = url[2]
            name = url[4]

        if name in blacklist:
            # logger.info("is core library")
            return True
        return False

    def parse(self, response):
        # self.logger.warning(response.meta)
        libraries = response.xpath('.//*[@class="inline Library"]')
        self.logger.warning("Lib counts: "+str(self.total_libs))
        for library in libraries:
            item = MbedParserLoader(item=MbedParserItem(), selector=library)
            item.add_xpath('commits',
                           '../../../../div[2]/div[1]/span[2]/span[1]/text()')
            item.add_xpath(
                'imports',
                '../../../../div[2]/div[1]//i[@class="imports fas fa-download"]/following-sibling::span[1]/text()'
            )
            item.add_xpath('name', 'a/text()')
            item.add_xpath('repo_url', 'a/@href')
            item.add_xpath('author_name', '../h5[1]/a/text()[1]')
            item.add_xpath('author_url', '../h5[1]/a/@href')
            item.add_xpath('description', '../../../p/text()')
            item.add_xpath('keywords', '../../../a/text()')
            library = item.load_item()
            # print(library)
            if int(library['commits']) < 1:
                self.logger.warning("Low commits rate")
                continue
            if int(library['imports']) < 5:
                self.stop = True
                self.logger.warning("Stop")
            if self.has_non_ascii_char(library['repo_url']):
                self.logger.warning("ascii error")
                continue
            if self.is_mbed_core_library(name=library['name']):
                self.logger.warning("is core lib")
                continue
            request = scrapy.Request(
                self.make_mbed_url(library['repo_url']),
                callback=self.parse_repository,
                dont_filter=True)
            request.meta['library'] = library
            yield request
        # if self.lib_page_cnt < self.lib_page_max:
            # Request next page of results
        next_page = response.css('li.paginate-next').get()
        self.logger.warning("Page: "+str(self.current_page))
        self.logger.warning("##################################")
        if next_page is not None and not self.stop:
            baseurl = response.url
            if 'baseurl' in response.meta:
                baseurl = response.meta['baseurl']

            self.current_page += 1
            request = scrapy.Request(
                baseurl + ('&page=%d' % self.current_page), dont_filter=True)
            # request.meta['pagenum'] = self.current_page
            request.meta['baseurl'] = baseurl
            yield request


    def is_fork(self, response):
        return response.xpath(
            './/*[@class="fa icon_repo_fork"]/../b/text()').extract()

    def get_file_extensions(self, response):
        files = set()
        for file in response.xpath(
                './/*[@class="fa fa-file-code-o"]//../text()').extract():
            files.add(file.split('.')[-1])
        return files

    def has_folders(self, response):
        return response.xpath(
            './/*[@class="fa fa-folder-open"]//../text()').extract()

    def parse_repository(self, response):
        library = response.meta['library']
        if self.is_fork(response):
            self.logger.warning(library['repo_url'] + ' is fork')
            return
        if not self.has_folders(response) and not (
                self.get_file_extensions(response) - set(['bld', 'lib'])):
            self.logger.warning(library['repo_url'] + ' folders and format error')
            return
        request = scrapy.Request(
            self.make_mbed_url(library['repo_url'] + "dependents"),
            callback=self.parse_examples,
            dont_filter=True)
        request.meta['library'] = library
        yield request

    def parse_examples(self, response):
        library = response.meta['library']
        examples = self.make_mbed_url(
            response.xpath(
                './/*[@class="contentitem"]//div[2]/div[2]/div/b/a/@href')
            .extract())
        library['examples'] = examples
        request = scrapy.Request(
            self.make_mbed_url(library['repo_url'] + "dependencies"),
            callback=self.parse_dependencies,
            dont_filter=True)
        request.meta['library'] = library
        yield request

    def parse_dependencies(self, response):
        library = response.meta['library']
        library['dependencies'] = []
        for dep in response.xpath('//*[@class="contentitem"]'):
            library['dependencies'].append({
                'name':
                dep.xpath('div[2]/div[2]/div/b/a/text()').extract()[0].strip(),
                'authors':
                dep.xpath('div[2]/div[2]/div/a/text()').extract()[0].strip(),
                "frameworks":
                "mbed"
            })
        self.total_libs += 1
        yield library