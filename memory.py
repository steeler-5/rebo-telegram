import json
import os
import re
from config import client

FACTS_FILE = "facts.json"
MEMORY_TRIGGERS = ["remember", "i am", "i'm", "i like", "i want", "i look forward to"]
HOBBY_KEYWORDS = [
    "reading", "writing", "drawing", "painting", "playing", "gaming", "coding",
    "working out", "exercising", "hiking", "biking", "cooking", "wildlife", "nature",
    "camping", "exploring"
]

def load_facts():
    if os.path.exists(FACTS_FILE):
        with open(FACTS_FILE, "r") as f:
            return json.load(f)
    return {}

def save_facts(facts):
    with open(FACTS_FILE, "w") as f:
        json.dump(facts, f, indent=4)

def fallback_llm_fact_extraction(message):
    prompt = f"""Extract a memory-worthy fact from this message. Respond in the format SaveFact: key = value. If none, say NONE.
Message: "{message}\""""
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )
    reply = response.choices[0].message.content.strip()
    if reply.lower().startswith("savefact:"):
        match = re.search(r"savefact:\s*(.*?)\s*=\s*(.+)", reply, re.IGNORECASE)
        if match:
            key = match.group(1).strip().lower().replace(" ", "_")
            value = match.group(2).strip()
            return key, value
    return None, None

def extract_fact(message):
    msg = message.lower()
    if msg.strip().endswith("?"):
        return None, None
    if any(t in msg for t in MEMORY_TRIGGERS) or any(h in msg for h in HOBBY_KEYWORDS):
        patterns = [
            r"(?:remember that )?(?:my|i am|i'm)\s+(.*?)\s+is\s+(.+)",
            r"i like(?: to)?\s+(.*?)(?:\.|$)",
            r"i want(?: to)?\s+(.*?)(?:\.|$)",
            r"i look forward to\s+(.*?)(?:\.|$)",
            r"i am\s+(.*?)(?:\.|$)",
            r"i'm\s+(.*?)(?:\.|$)"
        ]
        for pat in patterns:
            match = re.search(pat, message, re.IGNORECASE)
            if match:
                raw = match.group(1 if len(match.groups()) == 1 else 2)
                subject = re.sub(r"[^a-zA-Z0-9 ]", "", raw.strip().lower()).replace(" ", "_")
                value = match.group(2).strip() if len(match.groups()) == 2 else True
                return subject, value
    return fallback_llm_fact_extraction(message)

def build_memory_string(facts):
    return "\n".join([f"{k.replace('_', ' ')} is {v}." for k, v in facts.items()])

from datetime import datetime

def write_fact(key: str, value):
    print(f"[DEBUG] write_fact called with key='{key}', value='{value}'")
    facts = load_facts()
    timestamp = datetime.now().isoformat()
    facts[key.lower().replace(" ", "_")] = {
        "value": value,
        "timestamp": timestamp
    }
    save_facts(facts)
    print(f"[DEBUG] facts.json now contains:\n{json.dumps(facts, indent=4)}")
    return f"Saved: {key} = {value} (at {timestamp})"
