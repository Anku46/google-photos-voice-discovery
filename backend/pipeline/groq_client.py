import os
import time
import json
import groq
import instructor
from dotenv import load_dotenv
from datetime import datetime, date

# Load environment variables from .env file
load_dotenv(os.path.join(os.path.dirname(__file__), "..", "..", ".env"))

BUDGET_FILE = os.path.join(os.path.dirname(__file__), "..", "..", "data", "groq_budget.json")
MAX_DAILY_REQUESTS = 14000  # Groq free tier limit is around 14k req/day

def check_budget():
    """Checks the daily request budget. Raises an exception if exceeded to pause the run."""
    today = date.today().isoformat()
    
    if os.path.exists(BUDGET_FILE):
        with open(BUDGET_FILE, "r") as f:
            budget = json.load(f)
    else:
        budget = {"date": today, "requests": 0}
        
    if budget.get("date") != today:
        budget = {"date": today, "requests": 0}
        
    if budget["requests"] >= MAX_DAILY_REQUESTS:
        raise RuntimeError(f"Groq daily request budget exceeded ({MAX_DAILY_REQUESTS}). Run paused until tomorrow.")
        
    budget["requests"] += 1
    
    os.makedirs(os.path.dirname(BUDGET_FILE), exist_ok=True)
    with open(BUDGET_FILE, "w") as f:
        json.dump(budget, f)

def get_groq_client():
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY is not set. Please provide it in the .env file.")
    
    # Initialize native Groq client
    client = groq.Groq(api_key=api_key)
    
    # Patch with instructor for JSON schema extraction
    instructor_client = instructor.from_groq(client, mode=instructor.Mode.JSON)
    return instructor_client

def get_model(stage: str) -> str:
    """Returns the model ID for the given stage (filter, extract, classify, synthesize) from env."""
    model = os.environ.get(f"GROQ_MODEL_{stage.upper()}")
    if not model:
        raise ValueError(f"GROQ_MODEL_{stage.upper()} is not set in .env")
    return model

if __name__ == "__main__":
    try:
        client = get_groq_client()
        check_budget()
        print("Groq API client configured successfully.")
    except Exception as e:
        print(f"Error: {e}")
