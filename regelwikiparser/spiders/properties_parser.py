import re
import logging


class PropertiesParser(object):

    """docstring for PropertiesParser"""

    def __init__(self, info, spell_class):
        super(PropertiesParser, self).__init__()
        self.info = info
        self.spell_class = spell_class

    def filterPropertiesText(self, text, prop_rx):
        # filter unnessary html format stuff
        replace_operations = [
            r"</?div( \w+\=\".+?\")?>",
            r"</?span( \w+\=\".+?\")?>",
            r"<p>\s*</p>",
            r"<h1>(.*)</h1>"
        ]
        for op in replace_operations:
            text = re.sub(op, "", text, 0, re.U)

        # remove the strongs
        str_rx = r"\s*<strong>\s*" + prop_rx + r":?\s*</strong>\s*:?\s*"
        text = re.sub(str_rx, r"\1: ", text, 0, re.U)

        # parse the Publikation
        pub_rx = r"(<p>)?.*Publikation:\s?([\w\d ]+).*(</p>)?"
        m = re.search(pub_rx, text, re.U)
        if m is not None:
            publication = m.group(2)
        else:
            publication = None

        # filter out end keywords
        end_keywords = [
            r"Zaubererweiterungen",
            r"Publikation"
        ]
        end_rx = r"("
        for key in end_keywords[:-1]:
            end_rx += key + r"|"
        end_rx += end_keywords[-1] + r")(.|\n)*"
        text = re.sub(end_rx, "", text, 0, re.U)

        return (text, publication)

    def createPropRegEx(self, properties):
        prop_rx = r"("
        for key in properties[:-1]:
            prop_rx += key + r"|"
        prop_rx += properties[-1] + r")\s*"
        return prop_rx

    def filterProp(self, prop):
        prop_operations = [
            r"^((<p>)?\s*((</?p>)|(</?br>)))+",
            r"((<p>)?\s*((</?p>)|(</?br>)))+$"
        ]
        for rx in prop_operations:
            prop = re.sub(rx, "", prop, 0, re.U)
        return prop

    def parseByText(self, selector, item):
        props = self.info["properties"]
        spell_properties = {}

        # create a or regex of all properties
        prop_rx = self.createPropRegEx(props)

        # get the text of the selector
        text = selector.extract_first()
        # text = unicode(text, "utf-8")
        # use unicode fag everywhere! (re.U (Unicode) flag)

        # filter unnessary html format stuff
        (text, pub) = self.filterPropertiesText(text, prop_rx)
        spell_properties["Publikation"] = pub

        prop_rx += r": "

        # find the existing properties
        found_props = re.findall(prop_rx, text, re.U)

        # split the text by the properties
        found_descr = re.split(prop_rx, text)

        first_found = -1
        # iterate over the found descriptions
        for idx, elem in enumerate(found_descr):
            # if the description matches a property
            if elem in found_props:
                first_found = idx if first_found < 0 else first_found
                # save the next description as its descritpion
                spell_properties[elem] = self.filterProp(found_descr[idx + 1])

        if self.info['pre-text'] is 1:
            if first_found > 0:
                descr = self.filterProp(found_descr[first_found - 1])
                spell_properties['Wirkung'] = descr
            else:
                logging.warning("Pre Text Error! " + item["name"])

        item["properties"] = spell_properties

    def parseProperties(self, selector, item):
        """parse the properties of a spell and returns it as a dict"""

        self.parseByText(selector, item)

        default = self.info["default-verbreitung"]
        if default:
            item["properties"]["Verbreitung"] = default

        # Verbreitung default cases
        if self.spell_class == "Zaubertrick":
            if "Anmerkung" in item["properties"]:
                item["properties"]["Verbreitung"] = item[
                    "properties"]["Anmerkung"]
                item["properties"].pop("Anmerkung", None)

        if "Verbreitung" not in item["properties"]:
            item["properties"]["Verbreitung"] = "Allgemein"

        # Merkmal default cases
        if "Merkmal" not in item["properties"]:
            item["properties"]["Merkmal"] = "Keines"

    def parseKarmaExtensions(self, selector, item):
        """parse the karma extensions of a liturgy and returns it as a dict"""

        karma_extensions = {}

        if self.info['extension'] is 1:
            extension_content_query = ".//em[contains(.,'#')]/" + \
                "following-sibling::text()[1]"
            extension_title_query = ".//em/text()[contains(.,'#')]"
            title_selector = selector.xpath(extension_title_query)
            content_selector = selector.xpath(extension_content_query)
            titles = title_selector.extract()
            contents = content_selector.extract()
            if len(titles) >= 2 and len(contents) >= 2:
                for i in range(0, 3):
                    karma_extensions[i] = (titles[i][1:], contents[i])
            else:
                logging.warning("No Spell extensions found!")

        item['karmaextensions'] = karma_extensions

    def parseSpellExtensions(self, selector, item):
        """parse the spell extensions of a spell and returns it as a dict"""

        spell_extensions = {}

        if self.info['extension'] is 1:
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
