# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class StoryItem(scrapy.Item):
    hn_id = scrapy.Field()
    title = scrapy.Field()
    url = scrapy.Field()
    domain = scrapy.Field()
    points = scrapy.Field()
    submitted_by = scrapy.Field()
    submitted_ago = scrapy.Field()
    comment_count = scrapy.Field()
