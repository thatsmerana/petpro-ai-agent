from ..prompts import DECISION_MAKER_DESC, decision_maker_instruction
from ..config import CURRENT_DATE, gemini_model
from google.adk.agents import LlmAgent
from .booking_sequential_agent import booking_sequential_agent

# Define the decision maker agent -- responsible for making administrative decisions.
#
# STRUCTURED JSON OUTPUT REQUIREMENT:
# This agent MUST output structured JSON via output_key "administrative_decision" containing:
# {
#   "should_invoke_workflow": true|false,
#   "customer_verified": true|false,
#   "customer_id": "uuid-or-null",
#   "pets_verified": true|false,
#   "pet_ids": ["uuid1", "uuid2"]|null,
#   "booking_id": "uuid-or-null",
#   "reasoning": "Clear explanation of decision and verification state found",
#   "action": "invoke_workflow|monitor_only|acknowledge"
# }
#
# CONTEXT PASSING TO BOOKING_SEQUENTIAL_AGENT:
# The verification flags (customer_verified, pets_verified, booking_id) extracted from
# conversation history are passed to booking_sequential_agent via conversation context.
# This enables downstream agents (customer_agent, pet_agent, booking_creation_agent) to:
# - Skip redundant API calls when customer/pets already verified
# - Prioritize update path when booking_id exists
#
# The agent analyzes conversation history to extract existing customer_id, pet_ids, and booking_id
# from previous agent outputs, then includes these in its structured output for optimization.
#
# DELEGATION LOGIC:
# - When should_invoke_workflow=true and confidence >= 85%, delegates to booking_sequential_agent
# - The booking_sequential_agent receives the full conversation context including verification flags
# - Decision maker does NOT call tools directly - only delegates to sub-agents
decision_maker_agent = LlmAgent(
    name="decision_maker_agent",
    model=gemini_model(),
    description=DECISION_MAKER_DESC,
    instruction=decision_maker_instruction(CURRENT_DATE),
    output_key="administrative_decision",
    sub_agents=[booking_sequential_agent]
)

agent = decision_maker_agent

__all__ = ["decision_maker_agent"]

