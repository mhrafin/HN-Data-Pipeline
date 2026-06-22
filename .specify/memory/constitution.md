<!--
== Sync Impact Report ==
Version change: (unversioned template) → 0.1.0
Modified principles: [NONE] — first-time fill from placeholders
Added sections:
  - I. Web Crawling Etiquette (NON-NEGOTIABLE)
  - Governance (with versioning policy and amendment procedure)
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

- Rate MUST NOT exceed 1 request per second (1 req/sec); exceeding this threshold
  triggers retry/backoff
- robots.txt MUST be obeyed before any crawl

## Governance

- This constitution supersedes all informal development practices
- Amendments MUST be documented with rationale, impact analysis, and a migration plan
- All PRs and reviews MUST verify compliance with this constitution
- Complexity MUST be justified by documenting a simpler alternative considered
  and explaining why it was rejected
- Versioning follows semantic versioning: MAJOR for incompatible governance
  changes, MINOR for new principles or material expansions, PATCH for
  clarifications and non-semantic refinements
- Compliance is reviewed at every specification and planning gate

**Version**: 0.1.0 | **Ratified**: 2026-06-22 | **Last Amended**: 2026-06-22
