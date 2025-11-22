from google.adk.agents import SequentialAgent
from .customer_agent import customer_agent
from .pet_agent import pet_agent
from .booking_creation_agent import booking_creation_agent

# Define the booking sequential agent -- orchestrates customer, pet, and booking creation agents in sequence.
booking_sequential_agent = SequentialAgent(
    name="booking_sequential_agent",
    description="Execute complete booking workflow: customer → pets → booking creation in sequence with shared state",
    sub_agents=[customer_agent, pet_agent, booking_creation_agent]
)

__all__ = ["booking_sequential_agent"]

