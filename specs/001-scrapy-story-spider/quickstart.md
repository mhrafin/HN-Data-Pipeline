# Quickstart: Story Spider Validation Guide

## Prerequisites

- Python 3.12+
- pip

## Setup

```bash
# Install dependencies
pip install scrapy sqlalchemy

# Verify Scrapy installed
scrapy version
```

## Validation Scenarios

### Scenario 1: Single-page crawl (FR-002, FR-006)

```bash
scrapy crawl hn_stories -a max_pages=1
```

**Expected**: Crawls `/news`, yields ~30 `StoryItem` objects, persists to SQLite. Every item has `title`, `url`, and at least one metadata field populated.

**Verify**: Check SQLite database:
```bash
sqlite3 hn_stories.db "SELECT COUNT(*) FROM stories;"
# → ~30
sqlite3 hn_stories.db "SELECT title, url, points FROM stories LIMIT 5;"
```

### Scenario 2: Multi-page crawl (FR-003)

```bash
scrapy crawl hn_stories -a max_pages=3
```

**Expected**: Crawls `/news`, `/news?p=2`, `/news?p=3` with 30s gaps. Stories from all 3 pages persisted with correct `page_number`.

**Verify**:
```bash
sqlite3 hn_stories.db "SELECT page_number, COUNT(*) FROM stories GROUP BY page_number;"
# → 1|30  2|30  3|30  (last page may have fewer)
```

### Scenario 3: 30s crawl delay (FR-004, Constitution I)

Run scenario 2 and inspect logs. Consecutive request timestamps must differ by ≥30s.

### Scenario 4: robots.txt compliance (FR-005)

Check that `ROBOTSTXT_OBEY = True` in settings. Crawl starts by fetching `https://news.ycombinator.com/robots.txt`.

### Scenario 5: Idempotent re-crawl (FR-008, FR-010)

```bash
scrapy crawl hn_stories -a max_pages=1
scrapy crawl hn_stories -a max_pages=1
```

**Expected**: Second run logs duplicates (title + url) in `story_dedup_log` table. No crash. Story count unchanged.

**Verify**:
```bash
sqlite3 hn_stories.db "SELECT COUNT(*) FROM story_dedup_log;"
# → ~30 (or exact number of dupes)
sqlite3 hn_stories.db "SELECT COUNT(*) FROM stories;"
# → same as after first run
```

### Scenario 6: Configurable crawl depth (FR-009)

```bash
scrapy crawl hn_stories -a max_pages=5
```

**Expected**: Crawls exactly 5 pages (or fewer if HN has fewer pages total). Stops at last page gracefully when `a.morelink` is absent.

### Scenario 7: Malformed HTML handling

Inject a malformed page (e.g., blank HTML) via a local file or mock. Spider must log the URL, error details, and terminate via `CloseSpider`.

## Database Schema Verification

```bash
sqlite3 hn_stories.db ".schema"
# Should show:
#   CREATE TABLE stories (
#     id INTEGER PRIMARY KEY AUTOINCREMENT,
#     hn_id VARCHAR NOT NULL UNIQUE,
#     title VARCHAR NOT NULL,
#     ...
#   );
#   CREATE TABLE story_dedup_log (...);
```

## Switching to PostgreSQL (future)

```bash
DATABASE_URL=postgresql://user:pass@localhost:5432/hn_news scrapy crawl hn_stories
```

No code changes required — only environment variable change.

## Reference

- Data model: [data-model.md](./data-model.md)
- Spider contracts: [contracts/spider-contract.md](./contracts/spider-contract.md)
