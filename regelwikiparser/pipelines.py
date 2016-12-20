# -*- coding: utf-8 -*-

from scrapy.exporters import JsonItemExporter


class JsonWithEncodingPipeline(object):

    def __init__(self):
        self.file = open('file.json', 'wb')
        self.exporter = JsonItemExporter(
            self.file, encoding='utf-8', ensure_ascii=False)
        self.exporter.start_exporting()

    def spider_closed(self, spider):
        self.exporter.finish_exporting()
        self.file.close()

    def process_item(self, item, spider):
        self.exporter.export_item(item)
        return item
