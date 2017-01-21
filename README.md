# DSA5RegelWikiParser

Scrapy Spider that crawls the DSA5 Regel Wiki "http://www.ulisses-regelwiki.de/"

# How to use

To start a spider and crawl the "DSA5 Regel Wiki" open a command prompt at the folder containing the `scrapy.cfg` file and put a spider to work

```
scrapy crawl spidername
```

## Spiders

Currently I implemented 2 spiders:

### magic

```
scrapy crawl magic
```

Crawls all links found in the subdirectories of [Zauber](http://www.ulisses-regelwiki.de/index.php/zauber.html)
So:

 * [Rituale](http://www.ulisses-regelwiki.de/index.php/za_rituale.html)
 * [Zaubersprüche](http://www.ulisses-regelwiki.de/index.php/za_zaubersprueche.html)
 * [Zaubertricks](http://www.ulisses-regelwiki.de/index.php/Zauber_Zaubertricks.html)

Used for the project: [DSA5SpellBook](http://www.ulisses-ebooks.de/product/202891/Spell-Book-Webapplikation) with the corresponding [github-project](https://github.com/theShmoo/DSA5SpellBook)

### skills

```
scrapy crawl skills
```

Crawls all links found in [Kampfsonderfertigkeiten](http://www.ulisses-regelwiki.de/index.php/sf_kampfsonderfertigkeiten.html)

# Contribute

The work is not complete yet and If you want to contribute feel free to do so! And I will do my best to support you.
