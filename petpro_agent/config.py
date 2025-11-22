# Shared configuration for agent modules
import datetime
from google.genai import types
from google.adk.models import Gemini

# Current date (ISO) used in prompt builders
CURRENT_DATE = datetime.datetime.now().strftime("%Y-%m-%d")

# Retry configuration to mitigate transient rate limit / server errors
RETRY_CONFIG = types.HttpRetryOptions(
    attempts=5,
    exp_base=7,
    initial_delay=1,
    http_status_codes=[429, 500, 503, 504],
)

def gemini_model(name: str = "gemini-2.5-flash-lite"):
    """Return a Gemini model instance with shared retry options."""
    return Gemini(model=name, retry_options=RETRY_CONFIG)

__all__ = ["CURRENT_DATE", "RETRY_CONFIG", "gemini_model"]

