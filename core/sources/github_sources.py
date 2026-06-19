GITHUB_COLLECTION_FREQUENCY = "daily"

GITHUB_SIGNALS = [
    "stars",
    "forks",
    "topics",
    "description",
    "recent_activity",
]

GITHUB_FILTERS = {
    "minimum_stars": 100,
    "relevant_topics": True,
    "recent_activity": True,
}

GITHUB_SOURCES = {
    "ai": {
        "source_type": "github",
        "category": "ai",
        "question": "What are builders building?",
        "targets": [
            {
                "name": "trending_ai_repositories",
                "query": "topic:artificial-intelligence topic:machine-learning stars:>100",
                "sort": "stars",
                "order": "desc",
            },
            {
                "name": "generative_ai_repositories",
                "query": "topic:generative-ai OR topic:llm OR topic:diffusion stars:>100",
                "sort": "updated",
                "order": "desc",
            },
            {
                "name": "fast_growing_ai_repositories",
                "query": "topic:ai pushed:>={date_window} stars:>100",
                "sort": "stars",
                "order": "desc",
            },
        ],
    },
    "cybersecurity": {
        "source_type": "github",
        "category": "cybersecurity",
        "question": "What are builders building?",
        "targets": [
            {
                "name": "security_tools",
                "query": "topic:cybersecurity OR topic:security-tools stars:>100",
                "sort": "stars",
                "order": "desc",
            },  
            {
                "name": "vulnerability_research",
                "query": "topic:vulnerability-research OR topic:exploit-development stars:>50",
                "sort": "updated",
                "order": "desc",
            },
            {
                "name": "defensive_security",
                "query": "topic:blueteam OR topic:detection-engineering OR topic:threat-hunting stars:>50",
                "sort": "updated",
                "order": "desc",
            },
        ],
    },
    "agent_frameworks": {
        "source_type": "github",
        "category": "agent_frameworks",
        "question": "What are builders building?",
        "targets": [
            {
                "name": "agent_frameworks",
                "query": "topic:agents OR topic:ai-agents OR topic:agent-framework stars:>50",
                "sort": "updated",
                "order": "desc",
            },
            {
                "name": "multi_agent_systems",
                "query": "topic:multi-agent OR topic:autonomous-agents stars:>50",
                "sort": "stars",
                "order": "desc",
            },
            {
                "name": "coding_agents",
                "query": "topic:coding-agent OR topic:software-engineering-agent stars:>50",
                "sort": "updated",
                "order": "desc",
            },
        ],
    },
    "automation": {
        "source_type": "github",
        "category": "automation",
        "question": "What are builders building?",
        "targets": [
            {
                "name": "workflow_automation",
                "query": "topic:automation OR topic:workflow-automation stars:>100",
                "sort": "stars",
                "order": "desc",
            },
            {
                "name": "browser_automation",
                "query": "topic:browser-automation OR topic:web-automation stars:>50",
                "sort": "updated",
                "order": "desc",
            },
            {
                "name": "rpa_and_ops_automation",
                "query": "topic:rpa OR topic:devops-automation stars:>50",
                "sort": "updated",
                "order": "desc",
            },
        ],
    },
    "developer_tools": {
        "source_type": "github",
        "category": "developer_tools",
        "question": "What are builders building?",
        "targets": [
            {
                "name": "developer_productivity",
                "query": "topic:developer-tools OR topic:productivity stars:>100",
                "sort": "stars",
                "order": "desc",
            },
            {
                "name": "cli_tools",
                "query": "topic:cli OR topic:terminal stars:>100",
                "sort": "stars",
                "order": "desc",
            },
            {
                "name": "code_quality_tools",
                "query": "topic:static-analysis OR topic:code-quality stars:>50",
                "sort": "updated",
                "order": "desc",
            },
        ],
    },
}
