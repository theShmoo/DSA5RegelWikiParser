import scrapy

class FightAbilities(scrapy.Spider):
  name = "fight"

  start_urls  = [
      'http://www.ulisses-regelwiki.de/index.php/sf_kampfsonderfertigkeiten.html'
    ]

  def parse(self, response):

    for a in response.css('nav.mod_navigation a'):
      name = a.css('a::attr(title)').extract_first()
      link = a.css('a::attr(href)').extract_first()
      if link is not None:
        ability = response.urljoin(link)
        yield scrapy.Request(ability, callback=self.parse_ability)

  def parse_ability(self, response):

    yield {
      'text': response.css('div.ce_text').extract()
    }