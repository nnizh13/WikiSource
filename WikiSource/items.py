# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class Entry(scrapy.Item):
    author = scrapy.Field()
    title = scrapy.Field()
    year = scrapy.Field()
    text = scrapy.Field()
