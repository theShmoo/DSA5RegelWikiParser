#!/usr/bin/env python
# -*- coding: utf-8 -*-
from scrapy import Spider, Request
from regelwikiparser.items import SpellItem, SpellClassItem

class Magic(Spider):
  name = "magic"

  def start_requests(self):
    rituals = "http://www.ulisses-regelwiki.de/index.php/za_rituale.html"
    spells = "http://www.ulisses-regelwiki.de/index.php/za_zaubersprueche.html"
    magic_tricks = "http://www.ulisses-regelwiki.de/index.php/Zauber_Zaubertricks.html"
    magic_classes  = {
        "Rituale": rituals,
        #"Zaubersprueche": spells,
        "Zaubertricks": magic_tricks
      }

    for class_name, url in magic_classes.iteritems():
      print("start with " + class_name)
      item = SpellClassItem()
      item['spellclass'] = class_name
      item['spells'] = []
      yield Request(
        url=url,
        callback=self.parse,
        meta={'item': item}
      )
      yield item


  def parse(self, response):

    spellclass_item = response.meta['item']
    for a in response.css('nav.mod_navigation a'):
      spell_name = a.css('a::attr(title)').extract_first()
      print(spell_name)
      link = a.css('a::attr(href)').extract_first()
      if link is not None:
        item = SpellItem()
        item['name'] = spell_name
        spell_link = response.urljoin(link)
        item['link'] = spell_link
        yield Request(
          spell_link,
          callback=self.parse_spell,
          meta={'spell': item}
        )
        spellclass_item['spells'].append(item)

  def parse_spell(self, response):

    spell_item = response.meta['spell']
    spell_item['properties'] = {}

    properties = [
      "Probe",
      "Wirkung",
      "Ritualdauer",
      "AsP-Kosten",
      "Reichweite",
      "Wirkungsdauer",
      "Zielkategorie",
      "Merkmal",
      "Verbreitung",
      "Steigerungsfaktor"
    ]

    #name_query = "//*/div/h1/text()"
    #selector = response.xpath(name_query)
    #name = selector.extract()

    for p in properties:
      p_query = "//*/p/strong[text() = '" + p + ":']/following-sibling::text()[1]"
      selector = response.xpath(p_query)
      spell_item['properties'][p] = str(selector.extract()).lstrip()
    yield spell
