# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy
import re

from scrapy.loader import ItemLoader
from scrapy.loader.processors import MapCompose, Join, TakeFirst, Compose
from w3lib.html import remove_entities

#
# for data distributed over more than one webpage:
#
# http://doc.scrapy.org/en/0.24/topics/request-response.html#topics-request-response-ref-request-callback-arguments

def strip_component(str):
    if str:
        strlist = str.strip().split('\n')
        if len(strlist): str= strlist[0]

        str = re.sub(r"\s+", " ", str.replace("\n", " ")).strip()
        return str

    return None


class CleanupList(object):

    def __call__(self, values):
        nvalues = []
        for value in values:
            if (value not in nvalues) and (value != ""):
                nvalues.append(value)
        if len(nvalues) == 1:
            return nvalues[0]
        if len(nvalues) == 0:
            return None
        return nvalues


class MbedLibLoader(ItemLoader):
    default_input_processor = MapCompose(strip_component)
    default_output_processor = CleanupList()

class MbedLibItem(scrapy.Item):
    # define the fields for your item here like:
    repo_type = scrapy.Field() # Program or Library
    name = scrapy.Field()
    authors = scrapy.Field()
    description = scrapy.Field()
    keywords = scrapy.Field()
    owner = scrapy.Field()
    ownerurl = scrapy.Field()
    repository = scrapy.Field()
    deplist1 = scrapy.Field()
    deplist2 = scrapy.Field()
    components = scrapy.Field()
    dependencies = scrapy.Field()
    examples = scrapy.Field()
    frameworks = scrapy.Field()
    platforms = scrapy.Field()
    pass

class MbedItem(scrapy.Item):
    # define the fields for your item here like:
    name = scrapy.Field(output_processor=Compose(lambda v: v[0]))
    description = scrapy.Field()
    keywords = scrapy.Field()     # use components (link-elements rather than text)
    authors = scrapy.Field()
    repository = scrapy.Field()
    frameworks = scrapy.Field()
    platforms = scrapy.Field()
    dependencies = scrapy.Field() # get from %libpage%/dependencies
    examples = scrapy.Field()     # get from %libpage%/dependents
    pass

