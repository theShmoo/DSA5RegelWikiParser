#!/usr/bin/env python
# -*- coding: utf-8 -*-
from scrapy.spiders import CrawlSpider
from scrapy.selector import Selector
from scrapy.http import Request
from regelwikiparser.items import SpellItem
import logging
import json


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

    def concatSelector(self, selector):
        s = ""
        node_contains_string = "./child::node()[count(*/self::strong)>0]"
        for index, node in enumerate(selector):
            if node.xpath(node_contains_string).extract():
                logging.warning("strong detected!")
                break
            content = node.xpath("./text()").extract()
            if isinstance(content, basestring):
                s += content.lstrip()
            elif len(content) > 0:
                s += content[0].lstrip()
        return s

    def hasParagraphType(self, selector, item):
        """uses the selector to check if the spell is easy to parse"""

        q = ".//strong/ancestor-or-self::p[1]"
        pars = selector.xpath(q)
        for index, node in enumerate(pars):
            num_x = node.xpath("count(./descendant::strong)")
            num_strings = num_x.extract_first()
            if num_strings is None or float(num_strings) != 1.0:
                print("Bad Spell: " + item['name'])
                print("Num Strongs: " + str(num_strings))
                return 0
        return 1

    def parsePropertiesWithParagraphType(self, selector, item):
        """parse all properties by paragraph type"""
        props = self.class_info[item['spellclass']]['properties']
        spell_properties = {}

        for p in props:
            q_strong = ".//strong[contains(.,\"" + p + ":\")]"
            select_strong = selector.xpath(q_strong)
            str_strong = select_strong.xpath("string(.)").extract_first()
            if str_strong is not None:
                q_all = "string(./ancestor-or-self::p[1])"
                pars = select_strong.xpath(q_all)
                str_all = pars.extract_first()
                str_all = str_all.replace(str_strong, "")
                spell_properties[p] = str_all
            else:
                logging.warning("Property " + p + " for " + item['name'] +
                                " not found")
                spell_properties[p] = ""

        item['properties'] = spell_properties

    def parseProperties(self, selector, item):
        """parse the properties of a spell and returns it as a dict"""

        properties = [
            "Probe",
            "Ritualdauer",
            "Zauberdauer",
            "AsP-Kosten",
            "Reichweite",
            "Wirkungsdauer",
            "Zielkategorie",
            "Merkmal",
            "Talent",
            "Verbreitung",
            "Steigerungsfaktor",
            "AP-Wert",
            "Volumen",
            "Voraussetzungen",
            "Schutzkreis",
            "Bannkreis",
            "Tierarten"
        ]

        spell_properties = {}

        s_class = item['spellclass']

        # first check the type of the formatting
        p_type = self.hasParagraphType(selector, item)

        if p_type is 1:
            self.parsePropertiesWithParagraphType(selector, item)
        else:
            if s_class is "Zaubertrick" or s_class is "Ahnenzeichen":

                properties.append("Anmerkung")
                # query for the "Wirkung"
                # replace text() with node() to get the node
                q = ".//text()[1]"
                trick_response = selector.xpath(q)
                e = trick_response.extract()
                # the third one is always(?) the Wirkung
                spell_properties["Wirkung"] = e[2]
            else:
                properties.append("Wirkung")

            for p in properties:
                p_query = ".//strong[contains(.,'" + p + ":')]" + \
                    "/following::node()"
                p_select = selector.xpath(p_query)
                if p_select:
                    s = self.concatSelector(p_select)
                    if p == "Anmerkung":
                        p = "Verbreitung"
                    spell_properties[p] = s

            if s_class is "Stabzauber" or \
                    s_class is "Bann und Schutzkreis":
                spell_properties["Verbreitung"] = "Gildenmagier"

            if s_class is "Fluch" or s_class is "Vertrautentrick":
                spell_properties["Verbreitung"] = "Hexen"

            if s_class is "Dolchritual" or s_class is "Herrschaftsritual":
                spell_properties["Verbreitung"] = "Druiden"

            if s_class is "Elfenlied" or \
                    s_class is "Verzerrtes Elfenlied":
                spell_properties["Verbreitung"] = "Elfen"
            item['properties'] = spell_properties

    def parseSpellExtensions(self, selector, item):
        """parse the spell extensions of a spell and returns it as a dict"""

        spell_extensions = {}

        if self.class_info[item['spellclass']]['extension'] is 1:
            extension_content_query = ".//em[contains(.,'#')]/" + \
                "following-sibling::text()[1]"
            extension_title_query = ".//em/text()[contains(.,'#')]"
            title_selector = selector.xpath(extension_title_query)
            content_selector = selector.xpath(extension_content_query)
            titles = title_selector.extract()
            contents = content_selector.extract()
            if len(titles) >= 2 and len(contents) >= 2:
                for i in range(0, 3):
                    spell_extensions[i] = (titles[i][1:], contents[i])
            else:
                logging.warning("No Spell extensions found!")

        item['spellextensions'] = spell_extensions

    def parseName(self, selector, item):
        """tries to parse the name of spell and returns it as a string"""
        name_selector = selector.xpath(".//h1/text()")
        name = name_selector.extract_first()
        if name is None:
            logging.warning("No name found!")
        else:
            item['name'] = name

    def parseSpellClass(self, spell_class, item):
        """returns the already known spell class. (useless)"""

        if spell_class:
            item['spellclass'] = spell_class
        else:
            logging.warning("Spell Class not found!")

    def parseSpell(self, response):

        item = SpellItem()

        # save the link
        item['link'] = response.url

        # get the important divs (can be 2)
        importantDivs = "//div[@id='main']//div[contains(@class,'ce_text')]"
        i_select = response.xpath(importantDivs)

        # extract name
        self.parseName(i_select, item)

        # parse for spell class
        self.parseSpellClass(response.meta['type'], item)

        # parse for the properties
        self.parseProperties(i_select, item)

        # parse for the spell extensions
        self.parseSpellExtensions(i_select, item)

        return item
