from ..prompts import DECISION_MAKER_DESC, decision_maker_instruction
from ..config import CURRENT_DATE, gemini_model
from google.adk.agents import LlmAgent
from .booking_sequential_agent import booking_sequential_agent

# Define the decision maker agent -- responsible for making administrative decisions.
decision_maker_agent = LlmAgent(
    name="decision_maker_agent",
    model=gemini_model(),
    description=DECISION_MAKER_DESC,
    instruction=decision_maker_instruction(CURRENT_DATE),
    output_key="administrative_decision",
    sub_agents=[booking_sequential_agent]
)

__all__ = ["decision_maker_agent"]

