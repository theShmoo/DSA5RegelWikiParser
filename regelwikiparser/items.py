# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class SpellsItem(scrapy.Item):
    name = scrapy.Field()
    spells = scrapy.Field()

class SpellItem(scrapy.Item):
    name = scrapy.Field()
    properties = scrapy.Field()
    
class PropertyItem(scrapy.Item):
	properties = scrapy.Field()