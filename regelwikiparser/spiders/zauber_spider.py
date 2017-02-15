#!/usr/bin/env python
# -*- coding: utf-8 -*-
from scrapy.spiders import Spider
from scrapy.selector import Selector
from scrapy.http import Request
from regelwikiparser.items import SpellItem
import logging


class Magic(Spider):
    name = "magic"
    allowed_domains = ["ulisses-regelwiki.de"]
    base_url = "http://www.ulisses-regelwiki.de/index.php/"

    def start_requests(self):

        d = {
            "Flüche": "HSF_Hexenflueche.html",
            "Stabzauber": "SSF_Stabzauber.html",
            "Rituale": "za_rituale.html",
            "Zaubersprüche": "za_zaubersprueche.html",
            "Zaubertricks": "Zauber_Zaubertricks.html",
            "Elfenlieder": "ESF_Elfenlieder.html",
            "Ahnenzeichen": "Ahnenzeichen.html"
        }

        for key, link in d.iteritems():
            request = Request(self.base_url + link,
                              callback=self.parseNavItems)
            request.meta['type'] = key
            yield request

    def parseNavItems(self, response):
        xpath_mod_nav = "//*[@id='sub_header']//" + \
            "nav[contains(@class,'mod_navigation')]//" + \
            "a[@class='ulSubMenu']/@href"
        hxs = Selector(response=response, type="html")
        sites = hxs.xpath(xpath_mod_nav)
        for site in sites:
            url = self.base_url + site.extract()
            request = Request(url, callback=self.parseSpell)
            request.meta['type'] = response.meta['type']
            yield request

    def concatSelector(self, selector):
        s = ""
        for index, node in enumerate(selector):
            if node.xpath("self::strong").extract():
                logging.log(logging.WARNING, "strong detected!")
                break
            content = node.extract()
            if isinstance(content, basestring):
                s += content.lstrip()
            elif len(content) > 0:
                s += content[0].lstrip()
        return s

    def parseSpellClass(self, spell_class):
        if spell_class:
            return spell_class
        else:
            logging.log(logging.WARNING, "Spell Class not found!")

    def parseProperties(self, selector, spell_class):
        properties = [
            "Probe",
            "Ritualdauer",
            "Zauberdauer",
            "AsP-Kosten",
            "Reichweite",
            "Wirkungsdauer",
            "Zielkategorie",
            "Merkmal",
            "Verbreitung",
            "Steigerungsfaktor",
            "AP-Wert",
            "Volumen",
            "Voraussetzungen"
        ]

        spell_properties = {}

        if spell_class != "Zaubertrick":
            properties.append("Wirkung")
        else:
            properties.append("Anmerkung")
            # query for the "Wirkung"
            # replace text() with node() to get the node
            q = ".//text()[1]"
            trick_response = selector.xpath(q)
            e = trick_response.extract()
            # the third one is always(?) the Wirkung
            spell_properties["Wirkung"] = e[2]

        for p in properties:
            p_query = ".//strong[contains(.,'" + p + "')]" + \
                "/following-sibling::node()"
            p_select = selector.xpath(p_query)
            if p_select:
                s = self.concatSelector(p_select)
                if p == "Anmerkung":
                    p = "Verbreitung"
                spell_properties[p] = s

        return spell_properties

    def parseSpellExtensions(self, selector, spell_class):
        spell_extensions = {}

        if spell_class != 'Zaubertrick':

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
                logging.log(logging.WARNING, "No Spell extensions found!")

        return spell_extensions

    def parseSpell(self, response):

        item = SpellItem()

        importantDivs = "//div[@id='main']//div[contains(@class,'ce_text')]"
        i_select = response.xpath(importantDivs)

        # extract name
        name_selector = i_select.xpath(".//h1/text()")
        name = name_selector.extract_first()
        item['name'] = name

        # save the link
        item['link'] = response.url

        # parse for spell class
        spell_class = self.parseSpellClass(response.meta['type'])
        item['spellclass'] = spell_class

        # parse for the properties
        item['properties'] = self.parseProperties(i_select, spell_class)

        # parse for the spell extensions
        item['spellextensions'] = self.parseSpellExtensions(
            i_select, spell_class)

        return item
