import re


  # Topic Hierarchy
  
TOPIC_HIERARCHY = {

    "Artificial Intelligence": {

        "Agentic Systems": {

            "AI Agents": [
                "ai agent",
                "ai agents",
                "agentic ai",
                "agentic workflow",
                "agent framework",
                "autonomous agent",

                "langgraph",
                "crewai",
                "autogen",
                "pydanticai",
                "openai agents sdk",

                "mcp",
                "model context protocol",
            ]
        },

        "Local AI": {

            "Local LLMs": [
                "local llm",
                "local llms",
                "offline llm",
                "on-device llm",

                "ollama",
                "lm studio",
                "llama.cpp",
                "vllm",
            ]
        },

        "Knowledge Systems": {

            "RAG": [
                "rag",
                "retrieval augmented generation",

                "vector database",
                "embedding model",

                "pinecone",
                "qdrant",
                "weaviate",
                "chroma",
            ]
        },

        "Foundation Models": {

            "Large Language Models": [
                "llm",
                "llms",
                "large language model",
                "foundation model",

                "gpt",
                "claude",
                "gemini",
                "llama",
                "mistral",
            ]
        }
    },

    "Cybersecurity": {

        "Offensive Security": {

            "OSINT": [
                "osint",
                "open source intelligence",
                "social engineering",
            ],

            "Bug Bounty": [
                "bug bounty",
                "vulnerability research",
                "responsible disclosure",
            ],

            "Reverse Engineering": [
                "reverse engineering",
                "malware analysis",
                "binary analysis",
            ]
        },

        "Defensive Security": {

            "Threat Intelligence": [
                "threat intelligence",
                "ioc",
                "threat hunting",
            ],

            "Detection Engineering": [
                "detection engineering",
                "sigma",
                "edr",
                "siem",
            ],

            "Security Automation": [
                "security automation",
                "soar",
                "automated detection",
            ]
        }
    },

    "Automation": {

        "Workflow Automation": {

            "Browser Automation": [
                "browser automation",
                "playwright",
                "selenium",
            ],

            "RPA": [
                "rpa",
                "robotic process automation",
                "power automate",
            ]
        }
    },

    "Developer Ecosystem": {

        "Developer Tools": {

            "Developer Productivity": [
                "developer tools",
                "developer productivity",
                "devtools",
            ],

            "Code Quality": [
                "static analysis",
                "code quality",
                "linters",
            ]
        }
    },

    "Startups": {

        "Business Models": {

            "Vertical AI": [
                "vertical ai",
                "industry specific ai",
            ],

            "AI SaaS": [
                "ai saas",
                "saas",
            ]
        }
    }
}


  # Build Lookup Once
  
def build_lookup():

    lookup = {}

    for domain, themes in TOPIC_HIERARCHY.items():

        for theme, topics in themes.items():

            for topic, aliases in topics.items():

                for alias in aliases:

                    lookup[
                        alias.lower()
                    ] = {

                        "domain":
                            domain,

                        "theme":
                            theme,

                        "topic":
                            topic,

                        "entity":
                            alias,
                    }

    return lookup


LOOKUP = build_lookup()


  # Normalize Text
  
def normalize_text(text):

    text = (
        text or ""
    ).lower()

    matches = []
    seen_topics = set()

    for alias, info in LOOKUP.items():

        pattern = (
            rf"\b{re.escape(alias)}\b"
        )

        if not re.search(
            pattern,
            text
        ):
            continue

        unique_key = (
            info["domain"],
            info["theme"],
            info["topic"],
        )

        if unique_key in seen_topics:
            continue

        matches.append({

            "domain":
                info["domain"],

            "theme":
                info["theme"],

            "topic":
                info["topic"],

            "matched_entity":
                alias,
        })

        seen_topics.add(
            unique_key
        )

    return matches


  # Normalize Topic List
  
def normalize_topics(topic_list):

    results = []

    for topic in topic_list:

        results.extend(
            normalize_text(topic)
        )

    return results


  # Backward Compatibility
  
def normalize_topic(topic):

    matches = normalize_text(topic)

    if not matches:
        return topic

    return matches[0]["topic"]