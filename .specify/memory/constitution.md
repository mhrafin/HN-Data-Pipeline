<!--
== Sync Impact Report ==
Version change: 0.1.0 → 1.0.0
Modified principles:
  - I. Web Crawling Etiquette (NON-NEGOTIABLE): rate-limit rule redefined from
    1 req/s cap to 30s mandatory inter-request gap; added optimization
    constraint targeting 30s delay as primary design axis
Added sections: [NONE]
Removed sections: [NONE]
Templates requiring updates:
  - .specify/templates/plan-template.md: ✅ no changes needed (generic Constitution Check)
  - .specify/templates/spec-template.md: ✅ no changes needed (no principle-specific sections)
  - .specify/templates/tasks-template.md: ✅ no changes needed (no principle-specific task types)
  - .specify/templates/commands/: directory does not exist — skipped
  - README.md: ✅ no changes needed (no principle references)
Follow-up TODOs: [NONE]
-->

# HN-Data-Pipeline Constitution

## Core Principles

### I. Web Crawling Etiquette (NON-NEGOTIABLE)

All requests to the target domain MUST obey the following:

- A minimum of 30 consecutive seconds MUST elapse between the start
  of consecutive requests to the target domain
- This is a mandatory inter-request gap, not a per-second rate limit
- All system optimizations (batching, scheduling, parallelization) MUST
  be designed around this 30s crawl delay as the primary constraint
- robots.txt MUST be obeyed before any crawl begins

## Governance

- This constitution supersedes all informal development practices
- Amendments MUST be documented with rationale, impact analysis, and a
  migration plan
- All PRs and reviews MUST verify compliance with this constitution
- Complexity MUST be justified by documenting a simpler alternative
  considered and explaining why it was rejected
- Versioning follows semantic versioning: MAJOR for incompatible
  governance changes, MINOR for new principles or material expansions,
  PATCH for clarifications and non-semantic refinements
- Compliance is reviewed at every specification and planning gate

**Version**: 1.0.0 | **Ratified**: 2026-06-22 | **Last Amended**: 2026-06-22
