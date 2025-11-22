from ..prompts import CUSTOMER_AGENT_DESC, customer_agent_instruction
from ..config import CURRENT_DATE, gemini_model
from ..tools import get_customer_profile, create_customer
from google.adk.agents import LlmAgent

# Define the customer agent -- responsible for handling customer-related tasks.
customer_agent = LlmAgent(
    name="customer_agent",
    model=gemini_model(),
    description=CUSTOMER_AGENT_DESC,
    instruction=customer_agent_instruction(CURRENT_DATE),
    tools=[get_customer_profile, create_customer],
    output_key="customer_result"
)

__all__ = ["customer_agent"]

