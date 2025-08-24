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
        "PLAYWRIGHT_LAUNCH_OPTIONS": {"headless": True},
        "PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT": 60000,
    }

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(
                url,
                meta=dict(
                    playwright=True,
                    playwright_page_methods=[
                        PageMethod("wait_for_selector", "div[data-testid='list-card']"),
                        PageMethod("wait_for_timeout", 3000),
                    ],
                ),
                callback=self.parse,
            )

    def parse(self, response):
        # Zillow agent cards (check latest data-testid usage)
        cards = response.css("div[data-testid='list-card']")
        self.logger.info(f"Found {len(cards)} cards on {response.url}")

        for card in cards:
            name = card.css("h2::text").get()
            company = card.css("span:contains('Brokerage')::text").get()
            rating = card.css("span:contains('Rating')::text").get()
            reviews = card.css("span:contains('reviews')::text").get()

            yield {
                "name": name,
                "company": company,
                "rating": rating,
                "reviews": reviews,
            }

        # Handle pagination
        next_page = response.css("a[title='Next page']::attr(href)").get()
        if next_page:
            yield response.follow(
                next_page,
                meta=dict(
                    playwright=True,
                    playwright_page_methods=[
                        PageMethod("wait_for_selector", "div[data-testid='list-card']"),
                        PageMethod("wait_for_timeout", 3000),
                    ],
                ),
                callback=self.parse,
            )
