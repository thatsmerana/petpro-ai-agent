from ..prompts import PET_AGENT_DESC, pet_agent_instruction
from ..config import CURRENT_DATE, gemini_model
from ..tools import create_pet_profiles
from google.adk.agents import LlmAgent

# Define the pet agent -- responsible for handling pet-related tasks.
pet_agent = LlmAgent(
    name="pet_agent",
    model=gemini_model(),
    description=PET_AGENT_DESC,
    instruction=pet_agent_instruction(CURRENT_DATE),
    tools=[create_pet_profiles],
    output_key="pet_result"
)

__all__ = ["pet_agent"]

