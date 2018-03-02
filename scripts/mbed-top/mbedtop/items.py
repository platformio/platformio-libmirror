# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.loader import ItemLoader
from scrapy.loader.processors import MapCompose, Join, TakeFirst, Compose
import re


def strip_component(str):
    if str:
        strlist = str.strip().split('\n')
        str = ''
        if len(strlist) > 1:
            for s in strlist:
                str = str + s
        else:
            str = strlist[0]
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


class MbedParserLoader(ItemLoader):
    default_input_processor = MapCompose(strip_component)
    default_output_processor = CleanupList()


class MbedParserItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    commits = scrapy.Field()
    imports = scrapy.Field()
    author_name = scrapy.Field()
    author_url = scrapy.Field()
    name = scrapy.Field()
    description = scrapy.Field()
    repo_url = scrapy.Field()
    keywords = scrapy.Field()
    examples = scrapy.Field()
    dependencies = scrapy.Field()
