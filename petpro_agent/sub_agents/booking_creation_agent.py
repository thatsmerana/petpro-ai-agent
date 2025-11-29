from ..prompts import BOOKING_CREATION_DESC, booking_creation_agent_instruction
from ..config import CURRENT_DATE, gemini_model
from ..tools import ensure_booking_exists
from google.adk.agents import LlmAgent

# Define the booking creation agent -- responsible for handling booking-related tasks.
#
# STATE-AWARE TOOL USAGE:
# This agent uses ensure_booking_exists which handles all logic:
# - Gets customer_id and pet_ids from state (from customer_agent and pet_agent)
# - Gets service_id and service_rate_id from state (from service_agent)
# - Gets calculated dates from state (from date_calculation_agent)
# - Checks for existing bookings
# - Creates or updates booking as needed
# - Returns formatted JSON with booking_id and action_taken
#
# CONTEXT USAGE:
# - Input: Receives conversation context
# - Output: Returns structured JSON via output_key "booking_result" containing:
#   - customer_id, professional_id, pet_ids
#   - booking_id_from_history: booking_id if found in state
#   - existing_booking_found: "found_via_api|not_found"
#   - action_taken: "created|updated|no_changes"
#   - booking_id: Final booking UUID (created or updated)
#   - source: "api" indicating where booking_id came from
#
# The output is available to the root orchestrator and can be used in subsequent conversation turns.
# Note: date_calculation_agent is now a separate step in booking_sequential_agent, not a tool here.
booking_creation_agent = LlmAgent(
    name="booking_creation_agent",
    model=gemini_model(),
    description=BOOKING_CREATION_DESC,
    instruction=booking_creation_agent_instruction(CURRENT_DATE),
    tools=[ensure_booking_exists],
    output_key="booking_result"
)

__all__ = ["booking_creation_agent"]

