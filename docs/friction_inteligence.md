# Friction Intelligence Pipeline

## Mission

Transform large volumes of unstructured online discussions into a small set of verified, evidence-backed, and actionable frictions.

The pipeline exists to reduce noise while preserving evidence.

---

# Pipeline Overview

Raw Sources
↓
Collection
↓
Quality Filtering
↓
Relevance Filtering
↓
Complaint Extraction
↓
Friction Candidate Detection
↓
Evidence Aggregation
↓
Duplicate Clustering
↓
Cross-Source Validation
↓
Persistence Analysis
↓
Workaround Detection
↓
Solutionability Analysis
↓
Friction Validation
↓
Friction Reports

---

# Stage 1: Collection

## Purpose

Collect discussions from multiple sources.

## Inputs

* Reddit
* Hacker News
* GitHub Issues
* Product Forums
* Community Discussions
* Future Sources

## Outputs

Raw discussion records.

## Philosophy

Collect broadly.

Judge later.

---

# Stage 2: Quality Filtering

## Purpose

Remove low-quality content.

## Remove

* Spam
* Advertisements
* Link farms
* Bot content
* Extremely short posts
* Duplicated records

## Philosophy

Garbage in produces garbage out.

---

# Stage 3: Relevance Filtering

## Purpose

Remove content unrelated to friction discovery.

## Examples

Keep:

* Complaints
* Frustrations
* Pain points
* Questions
* Workarounds
* Operational problems

Remove:

* News
* Memes
* Announcements
* Personal updates

## Philosophy

Not every discussion contains useful friction signals.

---

# Stage 4: Complaint Extraction

## Purpose

Extract explicit and implicit expressions of difficulty.

## Examples

Explicit:

"This process takes hours."

Implicit:

"I ended up building a script because nothing worked."

## Output

Complaint records.

## Philosophy

Most people describe symptoms rather than problems.

---

# Stage 5: Friction Candidate Detection

## Purpose

Convert complaints into possible friction candidates.

## Example

Complaints:

* OAuth setup is confusing.
* OAuth documentation is terrible.
* OAuth takes hours.

Candidate:

OAuth setup complexity.

## Philosophy

Multiple complaints may describe the same underlying friction.

---

# Stage 6: Evidence Aggregation

## Purpose

Attach evidence to every candidate.

## Evidence

* URLs
* Quotes
* Timestamps
* Source metadata

## Philosophy

Every conclusion must be traceable.

---

# Stage 7: Duplicate Clustering

## Purpose

Group similar candidates together.

## Example

OAuth setup complexity

OAuth configuration confusion

OAuth onboarding difficulty

↓

Single friction cluster.

## Philosophy

The internet repeats itself.

The system should not.

---

# Stage 8: Cross-Source Validation

## Purpose

Check whether the same friction appears across independent communities.

## Examples

Reddit

GitHub

Hacker News

Forums

## Philosophy

Independent confirmation increases confidence.

---

# Stage 9: Persistence Analysis

## Purpose

Measure how long the friction survives.

## Questions

* Did it appear last week?
* Last month?
* Last quarter?

## Philosophy

Persistent problems are generally more valuable than temporary complaints.

---

# Stage 10: Workaround Detection

## Purpose

Identify attempts to bypass the friction.

## Examples

* Custom scripts
* Excel sheets
* Checklists
* Internal tools
* Manual processes

## Philosophy

Workarounds are strong evidence that a real problem exists.

---

# Stage 11: Solutionability Analysis

## Purpose

Determine whether the friction appears realistically addressable.

## Examples

Likely Solvable:

* Manual data entry
* CI/CD complexity
* Reporting workflows

Less Solvable:

* Political disagreement
* Personal preferences
* Human personality conflicts

## Philosophy

Not every problem can become action.

---

# Stage 12: Friction Validation

## Purpose

Final verification stage.

## Requirements

A friction should ideally have:

* Evidence
* Multiple mentions
* Independent validation
* Persistence
* Plausible solution path

## Philosophy

Verification before reporting.

---

# Stage 13: Friction Reports

## Purpose

Present verified frictions.

## Report Components

Friction Name

Summary

Evidence

Supporting Quotes

Sources

Persistence

Workarounds

Validation Notes

## Philosophy

Provide evidence.

Do not provide conclusions.

Do not recommend businesses.

Do not make decisions for the user.

The report exists to support human judgment.

---

# Final Principle

The system should never attempt to decide:

* What startup to build.
* What opportunity is best.
* What market will win.

The system's responsibility ends at:

Verified Friction

Human judgment begins afterward.




Collection
↓
Quality Filter
↓
Complaint Extraction
↓
Relevance Filter
↓
Friction Candidate Detection
↓
Evidence Aggregation
↓
Duplicate Clustering
↓
Cross-Source Validation
↓
Persistence Analysis
↓
Workaround Detection
↓
Solutionability Analysis
↓
Friction Validation
↓
Reports