import scrapy
from zillow_agents.items import ZillowAgentItem
from scrapy_playwright.page import PageMethod

class ChicagoAgentsSpider(scrapy.Spider):
    name = "chicago_agents"
    allowed_domains = ["zillow.com"]
    start_urls = ["https://www.zillow.com/professionals/real-estate-agent-reviews/chicago-il/?page=1"]

    custom_settings = {
        "DOWNLOAD_HANDLERS": {
            "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
            "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
        },
        "TWISTED_REACTOR": "twisted.internet.asyncioreactor.AsyncioSelectorReactor",
        "PLAYWRIGHT_BROWSER_TYPE": "chromium",
        "FEED_FORMAT": "csv",
        "FEED_URI": "agents.csv",
        "ROBOTSTXT_OBEY": False,
        "DOWNLOAD_DELAY": 1,
        "PLAYWRIGHT_LAUNCH_OPTIONS": {
            "headless": True,
        },
    }

    def start_requests(self):
        # Start from page 1
        yield from self.get_page_requests(1)

    def get_page_requests(self, page_number):
        url = f"https://www.zillow.com/professionals/real-estate-agent-reviews/chicago-il/?page={page_number}"
        yield scrapy.Request(
            url,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                              "AppleWebKit/537.36 (KHTML, like Gecko) "
                              "Chrome/139.0.0.0 Safari/537.36",
            },
            meta=dict(
                playwright=True,
                playwright_page_methods=[
                    PageMethod("wait_for_selector", "h2.Text-c11n-8-109-3__sc-aiai24-0")
                ],
                errback=self.errback,
                page_number=page_number
            )
        )

    def parse(self, response):
        agents = response.css("h2.Text-c11n-8-109-3__sc-aiai24-0::text").getall()
        if not agents:
            return  # Stop if no agents found on this page

        for name in agents:
            item = ZillowAgentItem()
            item["name"] = name.strip()
            yield item

        # Go to next page
        next_page_number = response.meta["page_number"] + 1
        yield from self.get_page_requests(next_page_number)

    def errback(self, failure):
        self.logger.error(repr(failure))
