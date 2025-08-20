import scrapy

class AgentItem(scrapy.Item):
    name = scrapy.Field()
    team_or_agent = scrapy.Field()
