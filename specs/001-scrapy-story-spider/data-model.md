# Data Model: Story Spider

## Entity: Story

The core entity representing a Hacker News submission on the `/news` page.

### Fields

| Field | Type | Source | Constraints | Notes |
|-------|------|--------|-------------|-------|
| `id` | Integer (PK, auto) | Generated | AUTOINCREMENT, unique | Internal DB primary key |
| `hn_id` | String | HTML `tr.athing#ID` | NOT NULL, UNIQUE | HN's story ID from the `id` attribute on the row |
| `title` | String | `td.title .titleline > a` text | NOT NULL | Full story title text |
| `url` | String | `td.title .titleline > a` href | NOT NULL, UNIQUE | The submitted URL (or `item?id=` for Ask HN etc.) |
| `domain` | String | `span.titleline > span.sitestr` text | NULLABLE | Domain as displayed on HN (e.g., `example.com`). NULL for self-posts (Ask HN, Show HN). |
| `points` | Integer | `span.score` text | NULLABLE | e.g., "123 points" → 123. NULL if score hidden/deleted. |
| `submitted_by` | String | `a.hnuser` text | NULLABLE | HN username of submitter. NULL for flagged/dead. |
| `submitted_ago` | String | `span.age` title attribute | NOT NULL | Raw relative time text (e.g., "2 hours ago") |
| `comment_count` | Integer | Comment link text | NULLABLE | e.g., "12 comments" → 12, "discuss" → 0, NULL if missing |
| `hn_position` | Integer | Row index on page | NOT NULL | 1-based position of story on the page |
| `page_number` | Integer | Page URL param `?p=N` | NOT NULL | Which page the story appeared on (1 = /news) |
| `created_at` | DateTime (ISO 8601) | Generated on insert | NOT NULL, default NOW() | When the record was inserted into the DB |

### Indexes

- `idx_story_url` — UNIQUE on `url` (dedup enforcement at DB level)
- `idx_story_hn_id` — UNIQUE on `hn_id` (secondary dedup)
- `idx_story_created_at` — for query ordering

### SQLAlchemy Model

```python
class Story(Base):
    __tablename__ = "stories"

    id = Column(Integer, primary_key=True, autoincrement=True)
    hn_id = Column(String, unique=True, nullable=False)
    title = Column(String, nullable=False)
    url = Column(String, unique=True, nullable=False)
    domain = Column(String, nullable=True)
    points = Column(Integer, nullable=True)
    submitted_by = Column(String, nullable=True)
    submitted_ago = Column(String, nullable=False)
    comment_count = Column(Integer, nullable=True)
    hn_position = Column(Integer, nullable=False)
    page_number = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)
```

### Validation Rules

1. `title` must not be empty
2. `url` must be a valid HTTP(S) URL (or relative `/item?id=` path)
3. `points` must be ≥ 0 when present
4. `hn_position` must be ≥ 1
5. `page_number` must be ≥ 1
6. Duplicate `url` → DB raises `IntegrityError` → pipeline logs duplicate and continues

### State Transitions

Story records are **insert-only** — no updates. A story appears once per crawl run and is never modified after insertion.

## Entity: StoryDedupLog (FR-010)

Audit log for duplicate story attempts.

| Field | Type | Constraints | Notes |
|-------|------|-------------|-------|
| `id` | Integer (PK, auto) | AUTOINCREMENT | Internal primary key |
| `url` | String | NOT NULL | The duplicate URL that was skipped |
| `title` | String | NOT NULL | The title of the duplicate story |
| `hn_id` | String | NULLABLE | HN story ID if available |
| `crawl_timestamp` | DateTime | NOT NULL, default NOW() | When the duplicate was encountered |
