# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import types

import json

# from support.py import *
from mbedtop.support import *
class JsonWriterPipeline(object):

    copykeys = [
        'name', 'description', 'keywords',
        'authors', 'repository', 'dependencies', 'examples',
        'frameworks', 'platforms'
    ]

    def process_item(self, item, spider):
        filename = item['name'] + '_' + item['owner']
        filename.replace(' ', '_')
        filename = "".join(x for x in filename if x.isalnum() or x=='_')

        path = "../../configs/mbed/"
        if is_mbed_core_library(name=item['name'], owner=item['owner']):
            path = "../../configs/mbed-core/"

            #TODO: Read existing file and add overwrite parsed fields only
            # so that moderated files do not lose information

        dirty = 0
        for key in pio_required_fields():
            if not key in item: dirty = 1
        if dirty:
            path = path + "moderation/"

        with open(path+filename+".json", "w") as f:
            print "####################  >>>  ",filename
            expo = self.copy_selected(item, self.copykeys)
            json.dump(dict(expo), f, indent=4, sort_keys=True, separators=(',', ': '))

        return item

    def copy_selected(self, item, keys):
        result = {}
        for key in keys:
            if key in item:
                result[key] = item[key]
        return result

class RepoPostProc(object):
    def process_item(self, item, spider):
        # prettify examples:
        if 'examples' in item:
            item['examples'] = make_mbed_url(item['examples'])[0:10]

        if 'repository' in item:
            repo = { "type" : "hg", "url" : make_mbed_url(item['repository']) }
            item['repository'] = repo

        if 'dependencies' in item:
            item['dependencies'] = make_mbed_url(item['dependencies'])

        if ('ownerurl' in item) and ('owner' in item):
            item['authors'] = { "name" : item['owner'], "url" : make_mbed_url(item['ownerurl']) }            

        if 'components' in item:
            authors = []
            keywords = []
            components = strip_mbed_url(item['components'])
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


