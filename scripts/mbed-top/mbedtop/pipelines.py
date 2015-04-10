# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import types

class RepoPostProc(object):
    def process_item(self, item, spider):
        #
        # transfer deplist1 and deplist2 to appropriate fields:
        #
	self.transfer_if(item,'deplist1','Dependencies:','dependencies')
        self.transfer_if(item,'deplist2','Dependencies:','dependencies')
        self.transfer_if(item,'deplist1','Dependents:','examples')
        self.transfer_if(item,'deplist2','Dependents:','examples')
        # sometimes there is a link to subpage instead of title "Dependencies":
        if ('repository' in item):
            rep = item['repository']
            if type(rep) is list: rep = rep[0]
            self.transfer_if(item,'deplist2',rep+'dependents','examples')

        # prettify examples:
        if ('examples' in item):
            item['examples'] = self.make_mbed_url(item['examples'])

        if ('repository' in item):
            repo = { "type" : "hg", "url" : self.make_mbed_url(item['repository']) }
            item['repository'] = repo

        if ('components' in item):
            authors = []
            keywords = []
            components = self.strip_mbed_url(item['components'])
            #if not type(components) is list: components = [ components ]
            for value in components:
                if '/teams/' in value: authors.append(value)
                if '/users/' in value: authors.append(value)
                if '/components/' in value: keywords.append(value.replace('/components/', '').replace('/', ''))
            #if len(authors): item['authors'] = authors
            if len(keywords): item['keywords'] = keywords
            del item['components']

        # todo: check components if contents need to go to authors or keywords

        return item

    def strip_mbed_url(self, resource):
        if isinstance(resource, types.StringTypes):
            resource = resource.replace("https://developer.mbed.org", "")
        elif type(resource) is list:
            for i, value in enumerate(resource):
                resource[i]= self.strip_mbed_url(value)
        return resource

    def make_mbed_url(self, resource):
        if isinstance(resource, types.StringTypes):
            if resource[0] == '/': 
                resource = "https://developer.mbed.org"+resource
        elif type(resource) is list:
            for i, value in enumerate(resource):
                resource[i]= self.make_mbed_url(value)
        return resource

    # transfer list in key1 to key2 (except first element) 
    # if first element equals firstval
    def transfer_if(self, item, key1, firstval, key2):
        if key1 in item.keys():
            if item[key1][0] == firstval:
                tmplist = item[key1]
                del tmplist[0]
                newlist = []
                if key2 in item:
                    newlist= item[key2]
                newlist = tmplist
                item[key2] = newlist
                del item[key1]
