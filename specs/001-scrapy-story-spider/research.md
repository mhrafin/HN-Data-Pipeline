# Research: Scrapy Story Spider

## 1. Scrapy Project Structure

**Decision**: Standard Scrapy project layout within a Python package (`hn_pipeline/`).

- **Scrapy** provides `scrapy startproject` but we'll manually create the structure for finer control.
- Spider classes extend `scrapy.Spider` (not `CrawlSpider`) — pagination is simple enough to handle manually.

## 2. Database Abstraction (SQLite → PostgreSQL)

**Decision**: SQLAlchemy ORM with declarative models.

- **SQLite** for development (file-based, zero config).
- **PostgreSQL** switch requires only changing `DATABASE_URL` in settings.
- SQLAlchemy `create_engine()` with `future=True` handles both backends.
- Use `scrapy.Item` as the in-pipeline data carrier; map to SQLAlchemy model in the pipeline.

**Rationale**: Single layer change (connection string) to switch databases; no code changes in spiders or pipelines.

**Alternatives considered**: raw `sqlite3` module (too coupled to SQLite, would require rewrite for PostgreSQL); Peewee ORM (less known, smaller ecosystem).

## 3. Hacker News /news Page Structure

- `/news` returns HTML with a `.athing` table containing story rows.
- Each `tr.athing` contains:
  - `td.title .titleline > a` — story link (title + URL)
  - `span.score` — points (e.g., "123 points")
  - `td.subtext` contains:
    - `a.hnuser` — submitter username (missing → dead/flagged story)
    - `span.age` — relative time (e.g., "2 hours ago")
    - comment link: `a` with text like "12 comments" or "discuss"
- Pagination: `a.morelink` at bottom → `/news?p=N+1`
- Last page: no `a.morelink` present
- Empty page: no `.athing` rows at all

**Selectors validated against**: current HN HTML structure (as of June 2026).

## 4. Duplicates Handling (FR-010)

**Decision**: Database-level uniqueness via `UNIQUE` constraint on story URL. Pipeline catches `IntegrityError` on insert, logs duplicate with title and URL, and continues.

- Scrapy's built-in dupe filter (`DUPEFILTER_CLASS`) operates on requests, not items — not suitable for story dedup across pages.
- The spec says "database enforces uniqueness — duplicate inserts are silently skipped" but FR-010 additionally requires logging duplicates. So pipeline will catch and log.

## 5. Retry & Error Handling

**Decision**: Use Scrapy's built-in `RetryMiddleware` with custom settings:
- `RETRY_TIMES = 3`
- `RETRY_HTTP_CODES = [429, 503]` (plus timeout handled by download timeout)
- Custom backoff via `DOWNLOAD_DELAY` + retry middleware `priority_adjust`
- Malformed HTML detection: post-parse validation in spider — if expected CSS selectors yield no results, log error with URL and HTML snippet, then `raise CloseSpider(reason)`.

## 6. Rate Limiting (Constitution I)

**Decision**: `DOWNLOAD_DELAY = 30` and `RANDOMIZE_DOWNLOAD_DELAY = False` to enforce exact 30s gap.
Also `CONCURRENT_REQUESTS_PER_DOMAIN = 1` to prevent any parallelization that could violate the 30s rule.

## 7. Testing Approach

**Decision**: `pytest` with `pytest-scrapy` for contract testing. Test pipelines with mock items, test spider parsing with saved HTML fixtures.

## Decisions Summary

| Concern | Decision | Rationale |
|---------|----------|-----------|
| Framework | Scrapy | Required by spec |
| ORM | SQLAlchemy | Future PostgreSQL migration |
| Testing | pytest + pytest-scrapy | Standard Scrapy testing |
| Dedup strategy | DB UNIQUE constraint + pipeline catch | Simplest, matches FR-010 |
| Pagination | Manual `response.css('a.morelink')` | Simple, no CrawlSpider needed |
| Malformed HTML | CloseSpider with logged details | Spec requirement |
