# Feature Specification: Scrapy Story Spider

**Feature Branch**: `001-scrapy-story-spider`

**Created**: 2026-06-22

**Status**: Draft

**Input**: User description: "Setup scrapy for the project to begin. Obeying everything from the constitution. First spider, StorySpider, crawling /news and it has pagination like /news?p=2"

## Clarifications

### Session 2026-06-22

- Q: What structured format should scraped story data be output as? → A: Store in SQLite initially, migrate to PostgreSQL later.
- Q: Should the scraper deduplicate stories across the entire multi-page crawl? → A: No dedup in the scraper; database enforces uniqueness — duplicate inserts are silently skipped.
- Q: How should the scraper handle transient HTTP errors (429, 503, timeout)? → A: 3 retries with exponential backoff starting at 30s (30s → 60s → 120s), then abort the page after exhaustion.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Scrape Front Page of /news (Priority: P1)

A developer runs the scraper and it fetches the first page of Hacker News /news, extracting story data (titles, URLs, points, authors, comment counts, timestamps) and outputting it in a structured format.

**Why this priority**: This is the core functionality — without successful single-page scraping there is no pipeline.

**Independent Test**: Can be verified by running the scraper against /news and confirming structured output contains the expected number of stories from the first page.

**Acceptance Scenarios**:

1. **Given** the scraper has been configured for the HN domain, **When** the developer initiates a crawl starting at /news, **Then** the first page of stories is fetched and each story's title, URL, and metadata are captured.
2. **Given** the scraper has completed a crawl of /news, **When** the developer inspects the output, **Then** every story on the page is present with no duplicates.

---

### User Story 2 - Multi-Page Pagination (Priority: P2)

The developer runs the scraper and it follows pagination links (/news?p=2, /news?p=3, etc.) to collect stories across multiple pages.

**Why this priority**: Pagination is essential for collecting more than the first 30 stories, which is the core value of a data pipeline.

**Independent Test**: Can be verified by running the scraper with a configured page limit and confirming output contains stories from the requested number of pages.

**Acceptance Scenarios**:

1. **Given** the scraper has finished crawling /news, **When** the developer configures a crawl depth of multiple pages, **Then** the scraper follows /news?p=N links up to the configured limit.
2. **Given** the scraper reaches the last available page of /news, **When** no further "More" link exists, **Then** the crawler terminates gracefully without error.

---

### User Story 3 - Polite Crawling with Rate Limiting (Priority: P2)

The developer runs the scraper and it respects the target domain's crawling policies by waiting between requests and obeying robots.txt.

**Why this priority**: HN is a shared community resource; aggressive crawling would harm the experience for other users and violate the project constitution.

**Independent Test**: Can be verified by observing request timestamps in logs — consecutive requests to the HN domain must be at least 30 seconds apart.

**Acceptance Scenarios**:

1. **Given** the scraper is crawling multiple pages, **When** consecutive requests are made to the HN domain, **Then** at least 30 seconds elapse between the start of each request.
2. **Given** robots.txt disallows certain paths, **When** the scraper resolves start URLs, **Then** it does not attempt to fetch disallowed paths.

---

### Edge Cases

- What happens when the network is unavailable or HN returns a non-200 status (e.g., 429, 503)?
- How does the system handle an empty page or a page with zero stories?
- How does the system handle malformed HTML or missing expected elements on the page?
- What happens when the "More" link is missing or malformed on the last page?
- How does the system behave when an unexpected pagination parameter is encountered?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The scraper MUST be structured as a configurable project that can be run on demand.
- **FR-002**: The scraper MUST fetch the Hacker News /news page and extract story data from it.
- **FR-003**: The scraper MUST support pagination via the /news?p=N query parameter for N >= 2.
- **FR-004**: The scraper MUST enforce a minimum 30-second gap between the start of consecutive requests to the HN domain.
- **FR-005**: The scraper MUST check and obey robots.txt before crawling.
- **FR-006**: The scraper MUST extract, at minimum, the story title and URL for each item on the page.
- **FR-007**: The scraper MUST retry transient HTTP errors (429, 503, timeout) up to 3 times with exponential backoff (30s, 60s, 120s), then abort the page and log the failure.
- **FR-008**: The scraper MUST persist scraped stories to a local database store, with each story as a record with consistent fields.
- **FR-009**: The scraper MUST support configurable crawl depth (maximum number of pages to traverse).
- **FR-010**: The scraper MUST use idempotent inserts so that re-storing an already-existing story is silently handled (no crash, no duplicate).

### Key Entities *(include if feature involves data)*

- **Story**: A Hacker News submission appearing on /news. Attributes include: title, URL, author, points, comment count, timestamp, position on page, and unique story ID. Persisted as a record in the database with uniqueness enforced by the database layer.
- **Page**: A single page of /news results. A page contains a list of stories and an optional link to the next page.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Developer can run the scraper against /news and receive structured output with all stories from the first page within 5 minutes (accounting for the 30s delay).
- **SC-002**: Developer can configure the scraper to crawl N pages and receive stories from all N pages in a single run.
- **SC-003**: Consecutive requests to the HN domain are always separated by at least 30 seconds (verified by request logs).
- **SC-004**: Every scraped story is persisted as a complete record (all expected fields populated) with 100% of accessible stories captured per page.
- **SC-005**: The scraper runs to completion without crashing on any page state (empty page, last page, network error).

## Assumptions

- HN's /news pagination uses the standard ?p=N convention and the "More" link follows this pattern.
- HN's robots.txt permits crawling of /news at the specified crawl delay.
- No authentication or session management is required to access /news.
- Target story fields (title, URL, author, points, comment count) are visible in the HTML of /news.
- A reasonable default crawl depth is 1 page; deeper crawling is opt-in via configuration.
- Error handling uses up to 3 retries with exponential backoff (30s / 60s / 120s) for transient network failures.
- Stories are expected to be roughly 30 per page, but the scraper adapts to the actual page content.
- Initial storage uses a lightweight local database, with a planned migration to a production-grade database system.
