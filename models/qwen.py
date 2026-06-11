# Imports

from ollama import chat

from interests_goals import (
    INTERESTS,
    GOALS
)


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
You are a personal trend intelligence analyst.

USER INTERESTS

{interest_text}

USER GOALS

{goal_text}

TASK

Analyze the article.

Return ONLY valid JSON.

Do not use markdown.

Do not use code fences.

Do not explain outside JSON.

Do not add text before or after JSON.

IMPORTANT

Return ONLY the TOP 5 most relevant interests.

Return ONLY the TOP 5 most relevant goals.

DO NOT return broad categories such as:

- Artificial Intelligence
- Cybersecurity
- Business
- Technology
- Psychology

Return specific topics from the interest list only.

SCORING

RELEVANCE

1 = Unrelated

3 = Slightly relevant

5 = Moderately relevant

7 = Strongly relevant

9 = Directly relevant

10 = Core topic


NOVELTY

1 = Very common

5 = Moderate innovation

10 = Potentially transformative


ACTIONABILITY

1 = Mostly theory

5 = Can be learned

8 = Can build products

10 = Immediate opportunity


LEARNING_VALUE

1 = Little educational value

3 = Basic knowledge

5 = Useful skill

7 = Strong capability gain

9 = Significant competitive advantage

10 = Major long-term leverage


MONETIZATION_POTENTIAL

1 = No obvious monetization

2 = Hobby income

3 = Freelance opportunity

4 = Side income

5 = Small business

6 = Strong niche business

7 = Startup potential

8 = Large market opportunity

9 = Category defining

10 = Billion-dollar potential


REQUIRED_COST

Estimate capital required to pursue
opportunities created by this article.

NOT the cost of patching.

1 = ₹0 - ₹1,000

2 = ₹1,000 - ₹10,000

3 = ₹10,000 - ₹50,000

4 = ₹50,000 - ₹1 lakh

5 = ₹1 lakh - ₹5 lakh

6 = ₹5 lakh - ₹25 lakh

7 = ₹25 lakh - ₹1 crore

8 = ₹1 crore - ₹10 crore

9 = ₹10 crore - ₹100 crore

10 = More than ₹100 crore


CLASSIFICATION

Determine:

- primary domain
- primary subcategory


Return EXACTLY this schema:

{{
    "overview": "...",

    "classification": {{
        "domain": "...",
        "subcategory": "..."
    }},

    "top_interests": [
        {{
            "topic": "...",
            "score": 0,
            "reason": "..."
        }}
    ],

    "top_goals": [
        {{
            "goal": "...",
            "score": 0,
            "reason": "..."
        }}
    ],

    "novelty": {{
        "score": 0,
        "reason": "..."
    }},

    "actionability": {{
        "score": 0,
        "reason": "..."
    }},

    "learning_value": {{
        "score": 0,
        "reason": "..."
    }},

    "monetization_potential": {{
        "score": 0,
        "reason": "..."
    }},

    "required_cost": {{
        "score": 0,
        "reason": "..."
    }},

    "key_points": [
        "...",
        "...",
        "..."
    ],

    "why_it_matters": "..."
}}

Article:

{content}
"""

    response = chat(
        model="qwen3:8b",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response.message.content