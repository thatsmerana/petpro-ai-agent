from ..prompts import BOOKING_CREATION_DESC, booking_creation_agent_instruction
from ..config import CURRENT_DATE, gemini_model
from ..tools import get_bookings, get_services, create_booking, update_booking
from google.adk.agents import LlmAgent

# Define the booking creation agent -- responsible for handling booking-related tasks.
#
# UPDATE VS CREATE PRIORITY LOGIC:
# This agent implements explicit priority logic to distinguish between booking updates and new bookings.
# The agent's system prompt (booking_creation_agent_instruction) enforces this priority order:
#
# PRIORITY 1: Check conversation history for booking_id
#   - If booking_id found in decision_maker_agent output or previous booking_creation_agent output
#   - → MUST use update_booking (after fetching full booking object via get_bookings)
#   - → Skip "check for overlapping bookings" logic
#
# PRIORITY 2: Check API for existing bookings (only if booking_id not in history)
#   - Call get_bookings to retrieve all existing bookings
#   - Look for overlapping bookings (same client + pets + overlapping dates + status="scheduled")
#   - If found → UPDATE path
#
# PRIORITY 3: Create new booking
#   - If no booking_id in history AND no overlapping booking found
#   - → CREATE new booking via create_booking
#
# This ensures database integrity by preventing duplicate bookings and correctly handling updates.
#
# CONTEXT USAGE:
# - Input: Receives conversation context including:
#   - customer_agent output (customer_result) with customer_id
#   - pet_agent output (pet_result) with pet_ids array
#   - decision_maker_agent output with booking_id (if exists)
# - Output: Returns structured JSON via output_key "booking_result" containing:
#   - customer_id, professional_id, pet_ids
#   - booking_id_from_history: booking_id if found in conversation history
#   - existing_booking_found: "found_in_history|found_via_api|not_found"
#   - action_taken: "created|updated|no_changes"
#   - booking_id: Final booking UUID (created or updated)
#   - source: "history|api" indicating where booking_id came from
#
# The output is available to the root orchestrator and can be used in subsequent conversation turns.
booking_creation_agent = LlmAgent(
    name="booking_creation_agent",
    model=gemini_model(),
    description=BOOKING_CREATION_DESC,
    instruction=booking_creation_agent_instruction(CURRENT_DATE),
    tools=[get_bookings, get_services, create_booking, update_booking],
    output_key="booking_result"
)

__all__ = ["booking_creation_agent"]

