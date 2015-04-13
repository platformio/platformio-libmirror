# -*- coding: utf-8 -*-

# Scrapy settings for mbedtop project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#

BOT_NAME = 'mbedtop'

SPIDER_MODULES = ['mbedtop.spiders']
NEWSPIDER_MODULE = 'mbedtop.spiders'
ITEM_PIPELINES = {
    'mbedtop.pipelines.RepoPostProc': 300,
    'mbedtop.pipelines.JsonWriterPipeline': 800,
}

# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'mbedtop (+http://www.yourdomain.com)'
