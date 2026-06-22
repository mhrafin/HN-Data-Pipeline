# Implementation Plan: Scrapy Story Spider

**Branch**: `001-scrapy-story-spider` | **Date**: 2026-06-22 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `specs/001-scrapy-story-spider/spec.md`

## Summary

Set up Scrapy project with a `StorySpider` that crawls Hacker News `/news` with pagination (`?p=N`), extracts story metadata (title, url, domain, points, submitter, age, comment count), and persists to SQLite via SQLAlchemy (enabling future PostgreSQL migration without code changes). Enforces 30s inter-request delay, obeys `robots.txt`, retries transient errors 3x with exponential backoff, and logs duplicates.

## Technical Context

**Language/Version**: Python 3.12+

**Primary Dependencies**: `scrapy`, `sqlalchemy`, `sqlalchemy-utils` (for PostgreSQL compatibility via SQLAlchemy abstraction)

**Storage**: SQLite via SQLAlchemy ORM; switchable to PostgreSQL by changing connection string only

**Testing**: `pytest` + `pytest-scrapy` (standard Scrapy testing approach)

**Target Platform**: Linux server

**Project Type**: CLI scraper (run via `scrapy crawl`)

**Performance Goals**: ~1 page per 30s (governed by constitution-mandated crawl delay); max crawl depth configurable

**Constraints**: 30s mandatory inter-request gap (NON-NEGOTIABLE); obey `robots.txt`; 3 retries with exponential backoff (30s, 60s, 120s) on 429/503/timeout; abort and log on malformed HTML

**Scale/Scope**: Hacker News `/news` pagination; ~30 stories/page; configurable page limit

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### I. Web Crawling Etiquette (NON-NEGOTIABLE)

| Requirement | Status | Evidence |
|---|---|---|
| 30s mandatory inter-request gap | ✅ PASS | FR-004 enforces `DOWNLOAD_DELAY = 30` |
| robots.txt obeyed | ✅ PASS | FR-005: Scrapy `ROBOTSTXT_OBEY = True` |
| Optimizations around 30s delay | ✅ PASS | Sequential single-threaded crawling; no batching/parallelism |

### Governance

| Requirement | Status | Evidence |
|---|---|---|
| Complexity justified with simpler alternatives | ✅ PASS | SQLAlchemy chosen over raw sqlite3 to enable future PostgreSQL switch — simplest abstraction layer meeting requirement |
| Compliance reviewed at planning gates | ✅ PASS | This gate evaluation |

**Result**: GATE PASSED — no violations. Complexity Tracking section not required.

## Project Structure

### Documentation (this feature)

```text
specs/001-scrapy-story-spider/
├── plan.md              # This file
├── spec.md              # Feature specification
├── research.md          # Phase 0: technology research & decisions
├── data-model.md        # Phase 1: entity definitions & relationships
├── quickstart.md        # Phase 1: validation guide
├── contracts/           # Phase 1: interface contracts
│   └── spider-contract.md
└── tasks.md             # Phase 2: implementation tasks (future)
```

### Source Code (repository root)

```text
hn_pipeline/
├── spiders/
│   └── story_spider.py      # StorySpider implementation
├── items.py                 # Scrapy Item definitions
├── pipelines.py             # Item Pipeline (DB persistence via SQLAlchemy)
├── middlewares.py            # Custom middlewares (if needed)
├── models.py                # SQLAlchemy ORM models
├── settings.py              # Scrapy project settings
└── db.py                    # Database engine/session management
```

## Complexity Tracking

> Not required — no constitution violations.
