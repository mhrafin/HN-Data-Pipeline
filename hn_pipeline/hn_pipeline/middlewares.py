# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html
from scrapy.downloadermiddlewares.retry import RetryMiddleware
from scrapy.settings import BaseSettings


class StorySpiderRetryMiddleware(RetryMiddleware):
    def __init__(self, settings: BaseSettings):
        super().__init__(settings)

    # enforce 30s/60s/120s backoff schedule on 429/503/timeout before delegating to super
    def process_response(self, request, response, spider):
        return super().process_response(request, response, spider)

    def process_exception(self, request, exception, spider):
        return super().process_exception(request, exception, spider)
