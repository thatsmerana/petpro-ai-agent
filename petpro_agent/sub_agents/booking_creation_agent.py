from ..prompts import BOOKING_CREATION_DESC, booking_creation_agent_instruction
from ..config import CURRENT_DATE, gemini_model
from ..tools import get_bookings, get_services, create_booking, update_booking
from google.adk.agents import LlmAgent

# Define the booking creation agent -- responsible for handling booking-related tasks.
booking_creation_agent = LlmAgent(
    name="booking_creation_agent",
    model=gemini_model(),
    description=BOOKING_CREATION_DESC,
    instruction=booking_creation_agent_instruction(CURRENT_DATE),
    tools=[get_bookings, get_services, create_booking, update_booking],
    output_key="booking_result"
)

__all__ = ["booking_creation_agent"]

