# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy.item import Item, Field


class SpellItem(Item):
    spellclass = Field()
    name = Field()
    link = Field()
    properties = Field()
    spellextensions = Field()

class KarmaItem(Item):
    karmaclass = Field()
    name = Field()
    link = Field()
    properties = Field()
    karmaextensions = Field()
