#!/usr/bin/env python
# -*- coding: utf-8 -*-
from scrapy.spiders import CrawlSpider
from scrapy.selector import Selector
from scrapy.http import Request
from regelwikiparser.items import SpellItem
from properties_parser import PropertiesParser
import json
import logging


class Magic(CrawlSpider):
    name = "magic"
    allowed_domains = ["ulisses-regelwiki.de"]
    base_url = "http://www.ulisses-regelwiki.de/index.php/"

    # load the spell infos from a file
    spell_info_file = "spellclassinfo.json"
    with open(spell_info_file) as json_data:
        class_info = json.load(json_data)

    def start_requests(self):
        for spell_class, data in self.class_info.iteritems():
            if data['active'] is 1:
                logging.info("Parsing links of " + spell_class)
                request = Request(self.base_url + data['link'],
                                  callback=self.parseNavItems)
                request.meta['type'] = spell_class
                yield request

    def parseNavItems(self, response):
        """Generator to create new requests of the start requests."""

        # The x path query to get all links inside the navigation of the site
        xpath_mod_nav = "//*[@id='sub_header']//" + \
            "nav[contains(@class,'mod_navigation')]//" + \
            "a[@class='ulSubMenu']/@href"
        hxs = Selector(response=response, type="html")

        # generate the requests from the selector
        sites = hxs.xpath(xpath_mod_nav)
        for site in sites:
            url = self.base_url + site.extract()
            request = Request(url, callback=self.parseSpell)
            request.meta['type'] = response.meta['type']
            yield request

    def parseSpell(self, response):

        item = SpellItem()

        # save the link
        item['link'] = response.url

        spell_class = response.meta['type']
        if spell_class:
            item['spellclass'] = spell_class
        else:
            logging.warning("Spell Class not found!")

        # get the important divs (can be 2)
        importantDivs = "//div[@id='main']//div[contains(@class,'ce_text')]"
        i_select = response.xpath(importantDivs)

        # create the properties parser
        pp = PropertiesParser(self.class_info[spell_class], spell_class)

        # extract the name
        pp.parseName(i_select, item)

        # extract the properties
        pp.parseProperties(i_select, item)

        # extract the spell extensions
        pp.parseSpellExtensions(i_select, item)

        return item
