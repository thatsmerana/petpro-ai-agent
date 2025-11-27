from ..prompts import PET_AGENT_DESC, pet_agent_instruction
from ..config import CURRENT_DATE, gemini_model
from ..tools import create_pet_profiles
from google.adk.agents import LlmAgent

# Define the pet agent -- responsible for handling pet-related tasks.
#
# SKIP LOGIC OPTIMIZATION:
# This agent implements skip logic to reduce redundant API calls for existing pets.
# The agent's system prompt (pet_agent_instruction) instructs the LLM to:
# 1. Check conversation history FIRST for pet verification state from decision_maker_agent
# 2. If pets_verified=true and pet_ids array exists in history, skip API calls and return existing IDs
# 3. Only proceed with create_pet_profiles API call if pets not found in history or need updates
# 4. Also checks customer_agent output for existing pets before creating duplicates
#
# CONTEXT USAGE:
# - Input: Receives conversation context including:
#   - customer_agent output (customer_result) with customer_id and existing_pets
#   - decision_maker_agent output with pets_verified flag and pet_ids array
# - Output: Returns structured JSON via output_key "pet_result" containing:
#   - customer_id: UUID from previous agent
#   - professional_id: Professional UUID from session context
#   - pet_ids: Array of pet UUIDs (existing or newly created)
#   - pet_names: Array of pet names
#   - status: "found|created|updated|found_in_history"
#   - source: "history|api" indicating where pet_ids came from
#
# The output is automatically available to downstream agent (booking_creation_agent)
# via Google ADK's SequentialAgent context passing mechanism.
pet_agent = LlmAgent(
    name="pet_agent",
    model=gemini_model(),
    description=PET_AGENT_DESC,
    instruction=pet_agent_instruction(CURRENT_DATE),
    tools=[create_pet_profiles],
    output_key="pet_result"
)

__all__ = ["pet_agent"]

