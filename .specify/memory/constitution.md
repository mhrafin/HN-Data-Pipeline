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

### II. No Architecture Decisions Without Approval (NON-NEGOTIABLE)

- No architecture decision MAY be implemented without explicit  
  verification and approval from the project owner
- Architecture decisions include: framework/library choices,  
  project structure, design patterns, data flow, storage backends,  
  and any cross-cutting technical direction
- Every proposal MUST document at least one simpler alternative  
  considered and explain why it was rejected

### III. Clean Code Discipline

- Code MUST follow clean code practices: meaningful names, small  
  focused functions, no commented-out code, minimal explanatory  
  comments where the code cannot self-document
- DRY principle MUST be followed — no duplication without explicit  
  justification
- Code MUST be self-documenting: naming, structure, and tests  
  should communicate intent, not comments
- Complexity MUST be justified as documented in the Governance section

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

**Version**: 1.1.0 | **Ratified**: 2026-06-22 | **Last Amended**: 2026-06-23
