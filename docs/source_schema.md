# Universal Intelligence Item Schema

All collectors should eventually output the same top-level structure so filters, analyzers, reporters, and future storage layers can work without caring where an item came from

## Canonical Shape

```json
{
  "source_type": "",
  "category": "",
  "title": "",
  "url": "",
  "content": "",
  "metadata": {},
  "analysis": null
}
```

## Field Definitions

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `source_type` | string | Yes | Origin system for the item. Expected values: `rss`, `github`, `reddit`, `hackernews`, `arxiv`. |
| `category` | string | Yes | Intelligence category such as `ai`, `cybersecurity`, `startups`, `developer_tools`, `research`, or `technology`. |
| `title` | string | Yes | Human-readable title, repository name, post title, story title, or paper title. |
| `url` | string | Yes | Canonical URL for the item. |
| `content` | string | Yes | Main text available to the analyzer. This may be article text, repository description/readme excerpt, post body, story text, or paper abstract. |
| `metadata` | object | Yes | Source-specific signals and collection context. Keep source-dependent fields here. |
| `analysis` | object or null | Yes | Analyzer output. Collectors should set this to `null`; analyzers populate it later. |

## Analysis Shape

Collectors should not generate analysis, but analyzers can populate this field using a consistent structure.

```json
{
  "overview": "",
  "tags": [],
  "importance": 1,
  "key_points": [],
  "why_it_matters": "",
  "opportunity_signals": [],
  "risk_signals": []
}
```

## Source Examples

### RSS

```json
{
  "source_type": "rss",
  "category": "cybersecurity",
  "title": "Major Vulnerability Discovered in Popular Remote Access Tool",
  "url": "https://example.com/security/vulnerability-report",
  "content": "Article text extracted from the source page...",
  "metadata": {
    "feed_url": "https://www.bleepingcomputer.com/feed/",
    "published_at": "2026-06-08T09:30:00Z",
    "author": "Example Author",
    "duplicate_key": "https://example.com/security/vulnerability-report",
    "content_length": 6420
  },
  "analysis": null
}
```

### GitHub

```json
{
  "source_type": "github",
  "category": "agent_frameworks",
  "title": "example-org/autonomous-agent-framework",
  "url": "https://github.com/example-org/autonomous-agent-framework",
  "content": "A framework for building autonomous AI agents with planning, tool use, memory, and evaluation support.",
  "metadata": {
    "owner": "example-org",
    "repository": "autonomous-agent-framework",
    "stars": 18400,
    "forks": 2100,
    "topics": ["ai-agents", "llm", "agent-framework", "automation"],
    "language": "Python",
    "created_at": "2025-11-14T12:10:00Z",
    "updated_at": "2026-06-07T18:45:00Z",
    "pushed_at": "2026-06-07T18:40:00Z",
    "open_issues": 87,
    "collection_target": "agent_frameworks"
  },
  "analysis": null
}
```

### Reddit

```json
{
  "source_type": "reddit",
  "category": "ai",
  "title": "What are people using local LLMs for every day?",
  "url": "https://www.reddit.com/r/LocalLLaMA/comments/example/post/",
  "content": "Post body describing user workflows, pain points, tools, and limitations...",
  "metadata": {
    "subreddit": "LocalLLaMA",
    "author": "example_user",
    "score": 1240,
    "upvote_ratio": 0.94,
    "comment_count": 312,
    "created_at": "2026-06-08T04:15:00Z",
    "flair": "Discussion",
    "engagement": {
      "upvotes": 1240,
      "comments": 312
    }
  },
  "analysis": null
}
```

### Hacker News

```json
{
  "source_type": "hackernews",
  "category": "developer_tools",
  "title": "Show HN: Lightweight observability for local AI agents",
  "url": "https://news.ycombinator.com/item?id=12345678",
  "content": "Story title and available story text. External URL: https://example.com/agent-observability",
  "metadata": {
    "hn_id": 12345678,
    "story_type": "show_hn",
    "external_url": "https://example.com/agent-observability",
    "score": 486,
    "comment_count": 141,
    "author": "example_founder",
    "created_at": "2026-06-08T10:20:00Z"
  },
  "analysis": null
}
```

### Arxiv

```json
{
  "source_type": "arxiv",
  "category": "research",
  "title": "Efficient Long-Context Reasoning for Tool-Using Language Agents",
  "url": "https://arxiv.org/abs/2606.01234",
  "content": "Paper abstract describing the method, experiments, and results...",
  "metadata": {
    "arxiv_id": "2606.01234",
    "categories": ["cs.AI", "cs.LG"],
    "primary_category": "cs.AI",
    "authors": ["Example Researcher", "Second Author"],
    "published_at": "2026-06-07T00:00:00Z",
    "updated_at": "2026-06-08T00:00:00Z",
    "pdf_url": "https://arxiv.org/pdf/2606.01234",
    "comment": "24 pages, 6 figures"
  },
  "analysis": null
}
```

## Design Notes

- Keep analyzer-facing fields stable at the top level.
- Put every source-specific signal in `metadata`.
- Keep `content` as the best available text for analysis, even when it is only a description, abstract, or post body.
- Leave `analysis` as `null` until an analyzer has processed the item.
- Prefer ISO 8601 timestamps for all dates in `metadata`.
