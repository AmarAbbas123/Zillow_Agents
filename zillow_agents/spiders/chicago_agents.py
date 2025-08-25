# chicago_agents.py
import scrapy
from scrapy_playwright.page import PageMethod

class ChicagoAgentsSpider(scrapy.Spider):
    name = "chicago_agents"
    allowed_domains = ["zillow.com"]
    start_urls = [
        "https://www.zillow.com/professionals/real-estate-agent-reviews/chicago-il/"
    ]

    custom_settings = {
        "DOWNLOAD_HANDLERS": {
            "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
            "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
        },
        "TWISTED_REACTOR": "twisted.internet.asyncioreactor.AsyncioSelectorReactor",
        "PLAYWRIGHT_LAUNCH_OPTIONS": {"headless": False},  # set False to debug visually
        "PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT": 60000,
    }

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(
                url,
                
            )

        # Inspecting Zillow agent pages → agent cards use <article> tags
       
