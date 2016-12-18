#!/usr/bin/env python
# -*- coding: utf-8 -*-
import scrapy

class Magic(scrapy.Spider):
  name = "magic"

  def start_requests(self):
    rituals = "http://www.ulisses-regelwiki.de/index.php/za_rituale.html"
    spells = "http://www.ulisses-regelwiki.de/index.php/za_zaubersprueche.html"
    magic_tricks = "http://www.ulisses-regelwiki.de/index.php/Zauber_Zaubertricks.html"
    magic_classes  = {
        "Rituale": rituals,
        "Zaubersprueche": spells,
        "Zaubertricks": magic_tricks
      }

    for class_name, url in magic_classes.iteritems():
      print("start with " + class_name)
      items[] = SpellsItem(name = class_name)
      yield scrapy.Request(url=url, callback=self.parse)

  def parse(self, response):

    for a in response.css('nav.mod_navigation a'):
      spell_name = a.css('a::attr(title)').extract_first()
      link = a.css('a::attr(href)').extract_first()
      if link is not None:
        spell_link = response.urljoin(link)
        yield scrapy.Request(spell_link, callback=self.parse_spell)

  def parse_spell(self, response):

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

    name_query = "//*/div/h1/text()"
    selector = response.xpath(name_query)
    name = selector.extract()

    item = PropertyItem()
    item['properties'] = {}
    for p in properties:
      p_query = "//*/p/strong[text() = '" + p + ":']/following-sibling::text()[1]"
      selector = response.xpath(p_query)
      item['properties'][p] = str(selector.extract()).lstrip()

    items[response.meta['class']][response.meta['name']]['properties'] = item