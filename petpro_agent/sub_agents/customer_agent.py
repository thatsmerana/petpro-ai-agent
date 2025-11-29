from ..prompts import CUSTOMER_AGENT_DESC, customer_agent_instruction
from ..config import CURRENT_DATE, gemini_model
from ..tools import ensure_customer_exists
from google.adk.agents import LlmAgent

# Define the customer agent -- responsible for handling customer-related tasks.
#
# STATE-AWARE TOOL USAGE:
# This agent uses ensure_customer_exists which handles all logic:
# - Checks state for existing customer
# - Calls API if needed
# - Creates customer if not found
# - Returns formatted JSON with customer_id and existing_pets
#
# CONTEXT USAGE:
# - Input: Receives conversation context
# - Output: Returns structured JSON via output_key "customer_result" containing:
#   - customer_id: UUID of found/created customer
#   - professional_id: Professional UUID from session context
#   - status: "found|created|insufficient_data"
#   - existing_pets: Array of pet objects (critical for next agent)
#   - source: "state|api" indicating where customer_id came from
#
# The output is automatically available to downstream agents (pet_agent, booking_creation_agent)
# via Google ADK's SequentialAgent context passing mechanism.
customer_agent = LlmAgent(
    name="customer_agent",
    model=gemini_model(),
    description=CUSTOMER_AGENT_DESC,
    instruction=customer_agent_instruction(CURRENT_DATE),
    tools=[ensure_customer_exists],
    output_key="customer_result"
)

__all__ = ["customer_agent"]

