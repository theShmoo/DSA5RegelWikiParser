#!/usr/bin/env python
# -*- coding: utf-8 -*-
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from regelwikiparser.items import SpellItem
import logging


class Magic(CrawlSpider):
    name = "magic"
    start_urls = ["http://www.ulisses-regelwiki.de/index.php/zauber.html"]
    allowed_domains = ["ulisses-regelwiki.de"]
    rules = (
        Rule(LinkExtractor(allow=('za_rituale\.html',
                                  'za_zaubersprueche\.html',
                                  'Zauber_Zaubertricks\.html'))),
        Rule(LinkExtractor(allow=('Rit_.*\.html')), callback='parseSpell'),
        Rule(LinkExtractor(allow=('ZT_.*\.html')), callback='parseSpell'),
        Rule(LinkExtractor(allow=('ZS_.*\.html')), callback='parseSpell'),
        Rule(LinkExtractor(allow=('SZ_.*\.html')), callback='parseSpell')
    )

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

    def parseSpellClass(self, response):
        short_url = response.url.rsplit('/', 1)[-1]

        if short_url.startswith('Rit_'):
            spell_class = 'Ritual'
        elif short_url.startswith('ZT_'):
            spell_class = 'Zaubertrick'
        elif short_url.startswith('ZS_') or short_url.startswith('SZ_'):
            spell_class = 'Zauberspruch'
        else:
            spell_class = 'Zauberspruch'
            logging.log(logging.WARNING, "Spell Class not found!")

        return spell_class

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
            "Steigerungsfaktor"
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
        spell_class = self.parseSpellClass(response)
        item['spellclass'] = spell_class

        # parse for the properties
        item['properties'] = self.parseProperties(i_select, spell_class)

        # parse for the spell extensions
        item['spellextensions'] = self.parseSpellExtensions(
            i_select, spell_class)

        return item
