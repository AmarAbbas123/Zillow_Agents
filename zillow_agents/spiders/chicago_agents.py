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
                meta=dict(
                    playwright=True,
                    playwright_page_methods=[
                        # wait for agent card wrapper (unique to agents page)
                        PageMethod("wait_for_selector", "article"),
                        PageMethod("wait_for_timeout", 5000),
                    ],
                ),
                callback=self.parse,
            )

    def parse(self, response):
        # Inspecting Zillow agent pages → agent cards use <article> tags
        cards = response.css("article")
        self.logger.info(f"Found {len(cards)} agent cards on {response.url}")

        for card in cards:
            name = card.css("h2::text").get()


            yield {
                "name": name,
               
            }

        # Pagination
        next_page = response.css("a[title='Next page']::attr(href)").get()
        if next_page:
            yield response.follow(
                next_page,
                meta=dict(
                    playwright=True,
                    playwright_page_methods=[
                        PageMethod("wait_for_selector", "article"),
                        PageMethod("wait_for_timeout", 5000),
                    ],
                ),
                callback=self.parse,
            )
