# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html
import time

from scrapy.downloadermiddlewares.retry import RetryMiddleware
from scrapy.settings import BaseSettings


class StorySpiderRetryMiddleware(RetryMiddleware):
    def __init__(self, settings: BaseSettings):
        super().__init__(settings)
        self.max_retry_times = settings.getint("RETRY_TIMES", 3)
        self.dl_delay = settings.getfloat("DOWNLOAD_DELAY", 0)

    def process_response(self, request, response, spider):
        if request.meta.get("dont_retry", False):
            return response
        if response.status in [429, 503]:
            result = self._retry_with_backoff(
                request, f"Status {response.status}", spider
            )
            return result if result is not None else response
        return super().process_response(request, response, spider)

    def process_exception(self, request, exception, spider):
        if request.meta.get("dont_retry", False):
            return None
        if isinstance(exception, self.RETRY_EXCEPTIONS):
            result = self._retry_with_backoff(request, str(exception), spider)
            return result if result is not None else None
        return None

    def _retry_with_backoff(self, request, reason, spider):
        retry_times = request.meta.get("retry_times", 0) + 1

        if retry_times <= self.max_retry_times:
            # Exponential backoff: 2^retry_times * dl_delay
            delay = 2 * self.dl_delay * retry_times
            spider.logger.info(
                f"Retrying {request.url} (attempt {retry_times}/{self.max_retry_times}) "
                f"after {delay}s delay. Reason: {reason}"
            )

            # Sleep before retry (not ideal but works for simple cases)
            # For production, use Scrapy's download delay settings instead
            time.sleep(delay)

            new_request = request.copy()
            new_request.meta["retry_times"] = retry_times
            new_request.dont_filter = True
            new_request.priority = request.priority - 1

            return new_request
        else:
            spider.logger.error(
                f"Gave up retrying {request.url} (failed {retry_times} times): {reason}"
            )
            return None
