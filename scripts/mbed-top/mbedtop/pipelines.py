# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import logging
import json
import hashlib
import codecs
import os
logging.basicConfig()
logger = logging.getLogger('mbed-pipeline-terrier')
# logger.setLevel("WARNING")


class MbedParserPipeline(object):

    def md5_file(self, fname):
        with open(fname, "rb") as f:
            hash_md5 = hashlib.md5(f.read())
        return hash_md5.hexdigest()

    def write_to_json_file(self, json_item):
        path = os.path.dirname(os.path.realpath(__file__))
        repo_tokens = json_item['repository']['url'].split('/')
        full_path = path + '/../../../configs/mbed/' + repo_tokens[6] + "_" + repo_tokens[4] + ".json"
        dumped_json = json.dumps(
                dict(json_item),
                indent=4,
                sort_keys=True,
                separators=(',', ': '),
                ensure_ascii=False)
        if os.path.isfile(full_path):
            md5_file = self.md5_file(full_path)
            md5_json = hashlib.md5(dumped_json.encode("utf-8")).hexdigest()
            if md5_file == md5_json:
                logger.warning("%s_%s.json already exist" % (repo_tokens[6],
                                                     repo_tokens[4]))
                return True
        with open(
                full_path,
                "w",
                encoding='utf-8') as f:
            logger.warning("Save to %s_%s.json  " % (repo_tokens[6],
                                                     repo_tokens[4]))
            f.write(dumped_json)


    def process_item(self, item, spider):
        json_item = {
            'authors': {
                'name': item['author_name'],
                'url': "https://os.mbed.com" + item['author_url']
            },
            'frameworks': 'mbed',
            'name': item['name'],
            'platforms': '*',
            'repository': {
                'type': 'hg',
                'url': "https://os.mbed.com" + item['repo_url']
            }
        }
        if item['dependencies']:
            json_item['dependencies'] = item['dependencies']
        if item['examples']:
            json_item['examples'] = item['examples']
        if 'description' in item:
            json_item['description'] = item['description']
        else:
            json_item['description'] = item['name']
        if 'keywords' in item:
            json_item['keywords'] = item['keywords']
        else:
            json_item['keywords'] = json_item['name']
        self.write_to_json_file(json_item)
