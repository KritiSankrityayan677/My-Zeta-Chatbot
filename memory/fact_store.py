import json, os

FACT_FILE = os.path.join(os.getcwd(), "user_facts.json")

def load_facts():
    if os.path.exists(FACT_FILE):
        try:
            with open(FACT_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_facts(facts: dict):
    try:
        with open(FACT_FILE, "w", encoding="utf-8") as f:
            json.dump(facts, f, indent=2)
    except Exception as e:
        print(f"[fact_store save error] {e}")

def update_fact(user: str, key: str, value: str):
    facts = load_facts()
    if user not in facts:
        facts[user] = {}
    facts[user][key] = value
    save_facts(facts)

def get_fact(user: str, key: str):
    facts = load_facts()
    return facts.get(user, {}).get(key)
