# Spider Contracts: StorySpider

## 1. Scrapy Item Contract

The spider yields `StoryItem` dict-like objects with the following schema:

```python
import scrapy

class StoryItem(scrapy.Item):
    hn_id = scrapy.Field()           # str: HN row ID from <tr id="...">
    title = scrapy.Field()           # str: story title
    url = scrapy.Field()             # str: story link href
    domain = scrapy.Field()          # str | None: parsed domain
    points = scrapy.Field()          # int | None: parsed from "N points"
    submitted_by = scrapy.Field()    # str | None: username
    submitted_ago = scrapy.Field()   # str: raw relative time text
    comment_count = scrapy.Field()   # int | None: parsed, 0 = "discuss"
```

## 2. Pipeline Contract

`StoryPipeline` receives `StoryItem` instances and persists them via SQLAlchemy.

```python
class StoryPipeline:
    """Item pipeline that persists StoryItems to the database.

    - Opens SQLAlchemy session on spider open
    - On item: maps StoryItem to Story ORM model, INSERT OR IGNORE
    - Catches IntegrityError, logs duplicate (title + url) to StoryDedupLog
    - Closes session on spider close
    """
```

## 3. Settings Contract

The Scrapy `settings.py` must expose:

| Setting | Type | Default | Purpose |
|---------|------|---------|---------|
| `DATABASE_URL` | str | `sqlite:///hn.db` | SQLAlchemy connection string |
| `DEFAULT_CRAWL_DEPTH` | int | `1` | Max pages to crawl |
| `STORYSPIDER_START_PAGE` | str | `/news` | Start URL path |

## 4. Spider Interface

```python
class StorySpider(scrapy.Spider):
    name = "hn_stories"

    def __init__(self, max_pages=None, *args, **kwargs):
        """max_pages: override crawl depth from command line"""

    def parse(self, response):
        """Parse a /news (or /news?p=N) page.
        Yields StoryItem for each story row.
        Follows a.morelink for next page if within max_pages.
        """

    def parse_story(self, row, page_number):
        """Extract a single StoryItem from a .athing tr element.
        Returns StoryItem or raises ValueError on malformed row.
        """
```

## 5. CLI Contract

```bash
# Run with default settings (1 page)
scrapy crawl hn_stories

# Run with custom page limit
scrapy crawl hn_stories -a max_pages=5

# Run with custom DB
DATABASE_URL=postgresql://user:pass@localhost/hn scrapy crawl hn_stories
```
