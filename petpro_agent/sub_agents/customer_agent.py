from ..prompts import CUSTOMER_AGENT_DESC, customer_agent_instruction
from ..config import CURRENT_DATE, gemini_model
from ..tools import get_customer_profile, create_customer
from google.adk.agents import LlmAgent

# Define the customer agent -- responsible for handling customer-related tasks.
#
# SKIP LOGIC OPTIMIZATION:
# This agent implements skip logic to reduce redundant API calls for returning customers.
# The agent's system prompt (customer_agent_instruction) instructs the LLM to:
# 1. Check conversation history FIRST for customer verification state from decision_maker_agent
# 2. If customer_verified=true and customer_id exists in history, skip API calls and return existing ID
# 3. Only proceed with get_customer_profile or create_customer API calls if customer not found in history
#
# CONTEXT USAGE:
# - Input: Receives conversation context including decision_maker_agent output with verification flags
# - Output: Returns structured JSON via output_key "customer_result" containing:
#   - customer_id: UUID of found/created customer
#   - professional_id: Professional UUID from session context
#   - status: "found|created|insufficient_data|found_in_history"
#   - existing_pets: Array of pet objects (critical for next agent)
#   - source: "history|api" indicating where customer_id came from
#
# The output is automatically available to downstream agents (pet_agent, booking_creation_agent)
# via Google ADK's SequentialAgent context passing mechanism.
customer_agent = LlmAgent(
    name="customer_agent",
    model=gemini_model(),
    description=CUSTOMER_AGENT_DESC,
    instruction=customer_agent_instruction(CURRENT_DATE),
    tools=[get_customer_profile, create_customer],
    output_key="customer_result"
)

__all__ = ["customer_agent"]

