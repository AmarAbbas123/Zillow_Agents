import scrapy

class ZillowAgentItem(scrapy.Item):
    name = scrapy.Field()  # Only scraping the name
