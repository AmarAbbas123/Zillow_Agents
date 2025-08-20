import scrapy
from scrapy_playwright.page import PageMethod   # ✅ new way

from ..items import AgentItem


class ZillowSpider(scrapy.Spider):
    name = "zillow"
    allowed_domains = ["zillow.com"]

    custom_settings = {
        "DOWNLOAD_HANDLERS": {
            "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
            "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
        },
        "TWISTED_REACTOR": "twisted.internet.asyncioreactor.AsyncioSelectorReactor",
        "PLAYWRIGHT_BROWSER_TYPE": "chromium",
        "PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT": 60000,
    }

    def start_requests(self):
        for page in range(1, 6):  # change 6 to how many pages you want
            url = f"https://www.zillow.com/professionals/real-estate-agent-reviews/chicago-il/?page={page}"
            yield scrapy.Request(
                url,
                meta=dict(
                    playwright=True,
                    playwright_page_coroutines=[
                        PageCoroutine("wait_for_selector", "h2"),  # wait for names to load
                    ],
                ),
            )

    def parse(self, response):
        agents = response.css("div[data-test='search-result']")
        for agent in agents:
            item = AgentItem()
            item["name"] = agent.css("h2::text").get()
            item["team_or_agent"] = agent.css("span.StyledTag-c11n-8-109-3__sc-1stu7t-0::text").get()
            yield item
