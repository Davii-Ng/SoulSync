import os
import random
from pathlib import Path

import requests
from dotenv import load_dotenv
from google.adk.agents.llm_agent import Agent

load_dotenv(Path(__file__).parent.parent / ".env")


def get_crisis_resources() -> dict:
    """Returns emergency mental health hotlines and crisis resources."""
    return {
        "status": "success",
        "resources": [
            {"name": "988 Suicide & Crisis Lifeline", "contact": "Call or text 988"},
            {"name": "Crisis Text Line", "contact": "Text HOME to 741741"},
            {"name": "NAMI Helpline", "contact": "1-800-950-6264"},
            {"name": "IMAlive Chat", "contact": "https://www.imalive.org"},
            {"name": "Trevor Project (LGBTQ+)", "contact": "1-866-488-7386 or text START to 678-678"},
        ],
    }


def get_therapist_resources() -> dict:
    """Returns links and tips for finding professional therapy."""
    return {
        "status": "success",
        "resources": [
            {"name": "Psychology Today Therapist Finder", "url": "https://www.psychologytoday.com/us/therapists"},
            {"name": "BetterHelp Online Therapy", "url": "https://www.betterhelp.com"},
            {"name": "Open Path Collective (affordable therapy)", "url": "https://openpathcollective.org"},
            {"name": "SAMHSA Treatment Locator", "url": "https://findtreatment.gov"},
        ],
    }


def get_mindfulness_exercise() -> dict:
    """Returns a short mindfulness or grounding exercise, randomly selected for variety."""
    exercises = [
        (
            "5-4-3-2-1 Grounding: Name 5 things you can see, "
            "4 you can touch, 3 you can hear, 2 you can smell, 1 you can taste."
        ),
        (
            "Box Breathing: Inhale for 4 seconds, hold for 4, "
            "exhale for 4, hold for 4. Repeat 4 times."
        ),
        (
            "Body Scan: Close your eyes. Starting from your toes, slowly move your attention "
            "up through your body. Notice any tension — don't fix it, just notice it."
        ),
        (
            "Cold Water Reset: Run cold water over your hands for 30 seconds. "
            "Focus on the sensation. It interrupts the stress response."
        ),
        (
            "3-3-3 Rule: Name 3 things you see, 3 sounds you hear, "
            "and move 3 parts of your body. It brings you back to right now."
        ),
    ]
    return {
        "status": "success",
        "exercise": random.choice(exercises),
    }


def search_local_resources(location: str, resource_type: str = "mental health therapist") -> dict:
    """Search for real mental health resources near the user's location.

    Args:
        location: The user's city, zip code, or general area (e.g. "Tampa, FL", "10001").
        resource_type: What to search for — e.g. "therapist", "support group", "psychiatrist".
    """
    query = f"{resource_type} near {location}"

    try:
        from html.parser import HTMLParser
        from urllib.parse import unquote

        class _ResultParser(HTMLParser):
            def __init__(self):
                super().__init__()
                self.in_result = False
                self.results = []
                self.current_url = ""

            def handle_starttag(self, tag, attrs):
                attrs_dict = dict(attrs)
                if tag == "a" and "result__a" in attrs_dict.get("class", ""):
                    self.in_result = True
                    raw = attrs_dict.get("href", "")
                    # Extract actual URL from DuckDuckGo redirect
                    if "uddg=" in raw:
                        self.current_url = unquote(raw.split("uddg=")[1].split("&")[0])
                    else:
                        self.current_url = raw

            def handle_data(self, data):
                if self.in_result:
                    self.results.append({"name": data.strip(), "url": self.current_url})
                    self.in_result = False

        resp = requests.get(
            "https://html.duckduckgo.com/html/",
            params={"q": query},
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=8,
        )
        if resp.status_code == 200:
            parser = _ResultParser()
            parser.feed(resp.text)
            if parser.results:
                return {
                    "status": "success",
                    "source": "web_search",
                    "resources": parser.results[:5],
                    "query": query,
                }
    except Exception:
        pass

    # Fallback: direct links
    return {
        "status": "success",
        "source": "fallback_links",
        "resources": [
            {"name": "Google Maps Search", "url": f"https://www.google.com/maps/search/{query.replace(' ', '+')}"},
            {"name": "Psychology Today Finder", "url": "https://www.psychologytoday.com/us/therapists"},
            {"name": "SAMHSA Treatment Locator", "url": "https://findtreatment.gov"},
            {"name": "Open Path Collective", "url": "https://openpathcollective.org"},
        ],
        "query": query,
        "note": "Could not search live results — here are direct links to find resources near you.",
    }


resource_agent = Agent(
    model="gemini-3-flash-preview",
    name="resource_agent",
    description=(
        "Provides mental health resources, crisis hotlines, therapist referrals, mindfulness exercises, "
        "and can search for real local resources near the user. "
        "Also activates when the user expresses frustration with the AI or asks for real/human help."
    ),
    instruction=(
        "STRICT RULE: 2-3 sentences max. No exceptions.\n\n"
        "You're the safety net, not the main act. Only show up when it really matters.\n"
        "Crisis → 'get_crisis_resources', share one number like a friend would.\n"
        "Wants real help → 'get_therapist_resources' or 'search_local_resources'.\n"
        "Needs to breathe → 'get_mindfulness_exercise', walk them through it briefly.\n"
        "Frustrated with AI → be honest about your limits, then find them a real person.\n\n"
        "Tone: calm, honest, no drama. You're handing them a lifeline, not giving a speech."
    ),
    tools=[get_crisis_resources, get_therapist_resources, get_mindfulness_exercise, search_local_resources],
)
