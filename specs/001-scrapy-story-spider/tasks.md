---
description: "Implementation tasks for the Scrapy Story Spider feature"
---

# Tasks: Scrapy Story Spider

**Input**: Design documents from `specs/001-scrapy-story-spider/`

**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/spider-contract.md, quickstart.md

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Key Design Decisions

- **Scaffolding**: Use `scrapy startproject hn_pipeline`, then manually restructure the generated directory to match plan.md layout. Do NOT create structure from scratch.
- **Domain extraction**: Extract from `titleline > span.sitestr` in the HTML — do NOT parse from URL.
- **Package management**: Use `uv` exclusively (uv add, uv sync, uv run). Never pip or venv.
- **Database**: SQLAlchemy ORM with SQLite for development; switchable to PostgreSQL via DATABASE_URL setting.

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and Scrapy project scaffolding

- [x] T001 Initialize Python project dependencies via `uv add scrapy sqlalchemy sqlalchemy-utils` in `pyproject.toml` at repo root
- [x] T001a Run `uv sync` to verify dependencies install cleanly before proceeding to scaffolding
- [x] T002 Run `scrapy startproject hn_pipeline` at repo root, then manually restructure the generated directory to match plan.md layout (items.py, pipelines.py, middlewares.py, models.py, db.py, settings.py, spiders/story_spider.py)
- [x] T003 Add `hn_stories.db` and `hn_stories.db-journal` to `.gitignore` at repo root

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure (database layer, Scrapy Items, settings) that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T004 Create SQLAlchemy ORM models (Story, StoryDedupLog) with all fields, constraints, and indexes per data-model.md in `hn_pipeline/models.py`
- [ ] T005 [P] Create Scrapy Item definitions (StoryItem) with all fields per spider-contract.md in `hn_pipeline/items.py`
- [ ] T006 Create database engine/session management with `create_engine` from `DATABASE_URL` setting, session factory, and `init_db()` in `hn_pipeline/db.py`
- [ ] T007 [P] Configure Scrapy settings in `hn_pipeline/settings.py` including `DOWNLOAD_DELAY=30`, `ROBOTSTXT_OBEY=True`, `CONCURRENT_REQUESTS_PER_DOMAIN=1`, `RANDOMIZE_DOWNLOAD_DELAY=False`, `DATABASE_URL`, `DEFAULT_CRAWL_DEPTH=1`, and `STORYSPIDER_START_PAGE="/news"`

**Checkpoint**: Foundation ready — database models, items, engine, and settings are all defined

---

## Phase 3: User Story 1 - Scrape Front Page of /news (Priority: P1) 🎯 MVP

**Goal**: The scraper fetches the first page of Hacker News `/news`, extracts story data (title, url, domain, points, submitter, age, comment count) and persists to SQLite.

**Independent Test**: Run `uv run scrapy crawl hn_stories -a max_pages=1` and verify ~30 stories are persisted in SQLite via `sqlite3 hn_stories.db "SELECT COUNT(*) FROM stories;"`

### Implementation for User Story 1

- [ ] T008 [US1] Implement StorySpider class with `name="hn_stories"`, start request to `/news`, and `parse` method that extracts stories from each `.athing` row using CSS selectors in `hn_pipeline/spiders/story_spider.py` — extract `hn_id` from `tr.athing` id attr, `title` and `url` from `span.titleline > a`, `domain` from `span.titleline > span.sitestr`, `points` from `span.score`, `submitted_by` from `a.hnuser`, `submitted_ago` from `span.age` title attr, `comment_count` from comment link text
- [ ] T009 [US1] Implement StoryPipeline with `open_spider` (create session), `process_item` (map StoryItem to Story ORM model, insert, catch IntegrityError and log duplicate to StoryDedupLog), and `close_spider` (close session) in `hn_pipeline/pipelines.py`
- [ ] T010 [US1] Wire up `ITEM_PIPELINES` with `StoryPipeline` and enable duplicate filter logging in `hn_pipeline/settings.py`

**Checkpoint**: At this point, User Story 1 should be fully functional. Run the independent test to verify ~30 stories persisted with all fields populated.

---

## Phase 4: User Story 2 - Multi-Page Pagination (Priority: P2)

**Goal**: The scraper follows pagination links (`/news?p=2`, `/news?p=3`) up to a configured page limit, collecting stories from all pages.

**Independent Test**: Run `uv run scrapy crawl hn_stories -a max_pages=3` and verify stories from pages 1, 2, and 3 are persisted with correct `page_number` via `sqlite3 hn_stories.db "SELECT page_number, COUNT(*) FROM stories GROUP BY page_number;"`

### Implementation for User Story 2

- [ ] T011 [US2] Add pagination logic to StorySpider `parse` method — detect `a.morelink`, extract `href` query param `?p=N+1`, yield `scrapy.Request` for next page if within `max_pages` limit, gracefully stop when no `a.morelink` exists
- [ ] T012 [US2] Add `max_pages` constructor arg to StorySpider (default from `DEFAULT_CRAWL_DEPTH` setting, overrideable via `-a max_pages=N`) and pass `page_number` metadata on each request for correct page tracking

**Checkpoint**: User Stories 1 AND 2 work. Multi-page crawl persists stories from all pages.

---

## Phase 5: User Story 3 - Polite Crawling with Rate Limiting (Priority: P2)

**Goal**: The scraper respects HN's crawling policies — 30s inter-request gap, robots.txt compliance, retry with exponential backoff on transient errors.

**Independent Test**: Run multi-page crawl and inspect logs — consecutive request timestamps to HN domain must be ≥30s apart. Verify `robots.txt` is fetched first.

### Implementation for User Story 3

- [ ] T013 [US3] Implement custom RetryMiddleware subclass in `hn_pipeline/middlewares.py` that overrides `process_response` and `process_exception` to enforce 30s/60s/120s backoff schedule on 429/503/timeout before delegating to super; register in `DOWNLOADER_MIDDLEWARES` in `hn_pipeline/settings.py` with `RETRY_TIMES=3`, `RETRY_HTTP_CODES=[429, 503]`
- [ ] T014 [US3] Add malformed HTML detection in `hn_pipeline/spiders/story_spider.py` — if `parse` finds zero `.athing` rows, log the URL with HTML snippet and raise `CloseSpider(reason="malformed_html")` to abort gracefully
- [ ] T015 [US3] Add structured logging in `hn_pipeline/pipelines.py` — log each story insertion with timestamp, log each duplicate skip (title + url), log pipeline open/close events for crawl audit trail

**Checkpoint**: All user stories independently functional with polite crawling, retry, error handling, and logging.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final verification and cleanup

- [ ] T016 [P] Verify all dependencies install cleanly with `uv sync` and run `uv run scrapy list` to confirm spider registration
- [ ] T017 Run quickstart.md validation scenarios end-to-end (single page, multi-page, idempotent re-crawl, DB schema verification)
- [ ] T018 Update this file (`specs/001-scrapy-story-spider/tasks.md`) with final status and any corrections discovered during implementation

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion — BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P2)
- **Polish (Phase 6)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) — No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) — Depends on US1's spider class but adds pagination to same file; logically sequential
- **User Story 3 (P2)**: Can start after Foundational (Phase 2) — Adds retry config and error handling to existing spider/pipeline; logically sequential

### Within Each User Story

- Models before services
- Core implementation before integration
- Story complete before moving to next priority

### Parallel Opportunities

- T005 and T007 can run in parallel (items.py + settings.py are independent files)
- All Phase 1 tasks are sequential (scaffolding depends on project init)
- User stories are designed as sequential increments for a single developer

---

## Parallel Example: Foundational Phase

```bash
# Launch independent foundational files in parallel:
Task: "Create Scrapy Items in hn_pipeline/items.py" (T005)
Task: "Configure Scrapy settings in hn_pipeline/settings.py" (T007)
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL — blocks all stories)
3. Complete Phase 3: User Story 1 (single-page scrape + SQLite persistence)
4. **STOP and VALIDATE**: Run independent test — `uv run scrapy crawl hn_stories -a max_pages=1`
5. Demo-ready: single-page scrape with persistence

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 (single-page scrape) → Test independently → Deploy/Demo (MVP!)
3. Add User Story 2 (pagination) → Test independently → Deploy/Demo
4. Add User Story 3 (polite crawling + retry + logging) → Test independently → Deploy/Demo
5. Each story adds value without breaking previous stories

### Validation Commands

```bash
# Phase completion checkpoints:
uv sync                                   # Verify dependencies
uv run scrapy list                        # Verify spider registered
uv run scrapy crawl hn_stories -a max_pages=1   # US1 validation
uv run scrapy crawl hn_stories -a max_pages=3   # US2 validation
sqlite3 hn_stories.db "SELECT COUNT(*) FROM stories;"  # Verify persistence
sqlite3 hn_stories.db "SELECT title, points, page_number FROM stories LIMIT 5;"  # Spot check
```

---

## Notes

- **[P]** tasks = different files, no dependencies — can run in parallel
- **[Story]** label maps task to specific user story for traceability
- Each user story is independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Use `uv` for all Python dependency management — never pip or venv
- Domain field: extract from `span.titleline > span.sitestr` text (strip parentheses), NOT parsed from URL
- Project structure: generated via `scrapy startproject` then manually restructured
