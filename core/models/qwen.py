# Imports

from ollama import chat

from interests_goals import INTERESTS, GOALS

# Build Interest Text

interest_text = ""

for category, topics in INTERESTS.items():

    interest_text += f"\n{category}\n"

    for topic in topics:

        interest_text += f"- {topic}\n"


# Build Goal Text

goal_text = ""

for goal in GOALS:

    goal_text += f"- {goal}\n"


# Analyze Article


def analyze(content):

    prompt = f"""
You are a trend intelligence analyst.

TASK
Analyze the article.
Return ONLY valid JSON.
Do not use markdown.
Do not use code fences.
Do not explain outside JSON.
Return EXACTLY this schema:

{{
    "summary": "...",
    "classification": {{
        "domain": "...",
        "subcategory": "..."
    }},
    "importance": {{
        "score": 0,
        "reason": "..."
    }},
    "key_points": [
        "...",
        "...",
        "..."
    ]
}}
SCORING

Importance:
1 = Not important
3 = Minor relevance
5 = Useful information
7 = Important development
9 = Major industry signal
10 = Potentially high-impact trend
ARTICLE

{content}
"""

    response = chat(model="qwen2.5:3b",
                     messages=[{"role": "user", "content": prompt}])
    return response.message.content
