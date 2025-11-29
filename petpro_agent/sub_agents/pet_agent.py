from ..prompts import PET_AGENT_DESC, pet_agent_instruction
from ..config import CURRENT_DATE, gemini_model
from ..tools import ensure_pets_exist
from google.adk.agents import LlmAgent

# Define the pet agent -- responsible for handling pet-related tasks.
#
# STATE-AWARE TOOL USAGE:
# This agent uses ensure_pets_exist which handles all logic:
# - Gets customer_id from state (from customer_agent)
# - Checks state for existing pets
# - Creates/updates pets if needed
# - Returns formatted JSON with pet_ids
#
# CONTEXT USAGE:
# - Input: Receives conversation context
# - Output: Returns structured JSON via output_key "pet_result" containing:
#   - customer_id: UUID from previous agent
#   - professional_id: Professional UUID from session context
#   - pet_ids: Array of pet UUIDs (existing or newly created)
#   - pet_names: Array of pet names
#   - status: "found|created|updated"
#   - source: "state|api" indicating where pet_ids came from
#
# The output is automatically available to downstream agent (booking_creation_agent)
# via Google ADK's SequentialAgent context passing mechanism.
pet_agent = LlmAgent(
    name="pet_agent",
    model=gemini_model(),
    description=PET_AGENT_DESC,
    instruction=pet_agent_instruction(CURRENT_DATE),
    tools=[ensure_pets_exist],
    output_key="pet_result"  # This is intermediate output - SequentialAgent should continue to booking_creation_agent
)

__all__ = ["pet_agent"]

