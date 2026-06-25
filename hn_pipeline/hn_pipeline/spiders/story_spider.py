from datetime import datetime

import scrapy
from scrapy.settings import Settings
from scrapy import Selector


class StorySpider(scrapy.Spider):
    name = "hn_stories"
    allowed_domains = ["news.ycombinator.com"]
    start_urls = ["https://news.ycombinator.com/news"]

    def __init__(self, max_pages: int = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        settings = Settings()
        self.max_pages: int = max_pages or settings.getint("DEFAULT_CRAWL_DEPTH", 1)
        self.pages_crawled = 0

    def parse(self, response):
        rows_tr = response.css("tr#bigbox > td > table tr")

        story_groups: list[list[Selector]] = []
        current_story = []
        counter = 0

        for row in rows_tr:
            if "spacer" in row.attrib.get("class", ""):
                counter += 1
                if current_story and counter <= 30:
                    story_groups.append(current_story)
                    current_story = []
            else:
                current_story.append(row)

        for story in story_groups:
            first_part = story[0]
            second_part = story[1]
            hn_id = first_part.attrib.get("id", "")
            title = first_part.css("span.titleline > a::text").get()
            url = first_part.css("span.titleline > a").attrib.get("href", "")
            domain = first_part.css("span.sitestr::text").get()
            points = second_part.css("span.score::text").get()
            submitted_by = second_part.css("a.hnuser::text").get()
            submitted_time_raw = second_part.css("span.age").attrib.get("title", "")

            # comments_count_raw = second_part.xpath(
            #     '//*[@id="bigbox"]/td/table/tr[2]/td[2]/span/a[3]//text()'
            # ).get()

            # comments_count_raw = second_part.xpath(
            #     '//span[@class="subline"]//a[contains(text(), "comment")]//text()'
            # ).get()
            comments_count_raw = second_part.css(
                '.subline a[href^="item?id"]::text'
            ).getall()[-1]
            yield {
                "hn_id": hn_id,
                "title": title,
                "url": url,
                "domain": domain,
                "points": points,
                "submitted_by": submitted_by,
                "submitted_time_raw": submitted_time_raw,
                "comments_count_raw": comments_count_raw,
            }
