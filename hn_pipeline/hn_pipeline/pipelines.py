# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from .models import Story, StoryDedupLog
from datetime import datetime
import re
from sqlalchemy.exc import IntegrityError


class StoryPipeline:
    def open_spider(self, spider):
        from .db import init_db, Session

        self.session = Session()
        init_db()

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)

        # Convert points to an integer if it exists
        if adapter.get("points"):
            match = re.search(r"(\d+)", adapter.get("points"))
            result = match.group() if match else None
            adapter["points"] = int(result) if result else 0
        else:
            adapter["points"] = 0

        # Convert submitted_time_raw to a datetime object if it exists
        if adapter.get("submitted_time_raw"):
            submitted_time = datetime.fromisoformat(
                adapter.get("submitted_time_raw").split(" ")[0]
            )
            adapter["submitted_time"] = submitted_time
        else:
            adapter["submitted_time"] = None

        # Get comments_count_raw and convert it to an integer if it exists
        # print(f"Raw comments count: {adapter.get('comments_count_raw')}")
        if adapter.get("comments_count_raw"):
            match = re.search(r"(\d+)", adapter.get("comments_count_raw"))
            # print(f"Match found: {match}")
            result = match.group() if match else None
            # print(f"Result: {result}")
            adapter["comments_count"] = int(result) if result else 0
            # print(f"Final comments count: {adapter['comments_count']}")
        else:
            adapter["comments_count"] = 0

        story = Story(
            hn_id=adapter.get("hn_id"),
            title=adapter.get("title"),
            url=adapter.get("url"),
            domain=adapter.get("domain"),
            points=adapter.get("points"),
            submitted_by=adapter.get("submitted_by"),
            submitted_time=adapter.get("submitted_time"),
            comment_count=adapter.get("comments_count"),
        )

        # Add the story to the database and handle duplicates
        try:
            self.session.add(story)
            self.session.commit()
            spider.logger.info(f"Story {story.hn_id} added to the database.")
        except IntegrityError:
            self.session.rollback()
            dup = StoryDedupLog(
                hn_id=adapter.get("hn_id"),
                title=adapter.get("title"),
                url=adapter.get("url"),
            )
            self.session.add(dup)
            self.session.commit()
            spider.logger.info(
                f"Story {story.hn_id} already exists. Added to dedup log."
            )

        return item

    def close_spider(self, spider):
        self.session.close()
