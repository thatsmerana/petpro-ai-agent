from .intent_classifier_agent import intent_classifier_agent
from .decision_maker_agent import decision_maker_agent
from .customer_agent import customer_agent
from .pet_agent import pet_agent
from .booking_creation_agent import booking_creation_agent
from .booking_sequential_agent import booking_sequential_agent

__all__ = [
    "intent_classifier_agent",
    "decision_maker_agent",
    "customer_agent",
    "pet_agent",
    "booking_creation_agent",
    "booking_sequential_agent",
]
import datetime
from google.genai import types
from google.adk.models import Gemini

# Centralized shared configuration for agents
CURRENT_DATE = datetime.datetime.now().strftime("%Y-%m-%d")

# Retry configuration for Gemini models to mitigate transient 429/5xx errors
RETRY_CONFIG = types.HttpRetryOptions(
    attempts=5,
    exp_base=7,
    initial_delay=1,
    http_status_codes=[429, 500, 503, 504],
)

# Helper to build a Gemini model with retry
def gemini_model(name: str = "gemini-2.5-flash-lite"):
    return Gemini(model=name, retry_options=RETRY_CONFIG)

__all__ = ["CURRENT_DATE", "RETRY_CONFIG", "gemini_model"]

