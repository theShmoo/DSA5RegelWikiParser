#!/usr/bin/env python
# -*- coding: utf-8 -*-
from scrapy.spiders import CrawlSpider
from scrapy.selector import Selector
from scrapy.http import Request
from regelwikiparser.items import KarmaItem
from properties_parser import PropertiesParser
import json
import logging


class Karma(CrawlSpider):
    name = "karma"
    allowed_domains = ["ulisses-regelwiki.de"]
    base_url = "http://www.ulisses-regelwiki.de/index.php/"

    # load the karma infos from a file
    karma_info_file = "karmaclassinfo.json"
    with open(karma_info_file) as json_data:
        class_info = json.load(json_data)

    def start_requests(self):
        for karma_class, data in self.class_info.iteritems():
            if data['active'] is 1:
                logging.info("Parsing links of " + karma_class)
                request = Request(self.base_url + data['link'],
                                  callback=self.parseNavItems)
                request.meta['type'] = karma_class
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
            request = Request(url, callback=self.parseKarma)
            request.meta['type'] = response.meta['type']
            yield request

    def parseKarma(self, response):

        item = KarmaItem()

        # save the link
        item['link'] = response.url

        karma_class = response.meta['type']
        if karma_class:
            item['karmaclass'] = karma_class
        else:
            logging.warning("Karma Class not found!")

        # get the important divs (can be 2)
        importantDivs = "//div[@id='main']//div[contains(@class,'ce_text')]"
        i_select = response.xpath(importantDivs)

        # create the properties parser
        pp = PropertiesParser(self.class_info[karma_class], karma_class)

        # extract the name
        pp.parseName(i_select, item)

        # extract the properties
        pp.parseProperties(i_select, item)

        # extract the karma extensions
        pp.parseKarmaExtensions(i_select, item)

        return item
