from ..prompts import SERVICE_AGENT_DESC, service_agent_instruction
from ..config import CURRENT_DATE, gemini_model
from ..tools import ensure_service_matched
from google.adk.agents import LlmAgent

# Define the service agent -- responsible for handling service-related tasks.
#
# STATE-AWARE TOOL USAGE:
# This agent uses ensure_service_matched which handles all logic:
# - Checks state for existing service match
# - Calls get_services if needed
# - Matches service semantically with improved logic
# - Validates service rate exists and extracts serviceRateId
# - Returns formatted JSON with service_id, service_name, service_rate_id, and service_rate
#
# CONTEXT USAGE:
# - Input: Receives conversation context
# - Output: Returns structured JSON via output_key "service_result" containing:
#   - service_id: UUID of matched service
#   - professional_id: Professional UUID from session context
#   - service_name: Name of the matched service
#   - service_rate_id: UUID of the service rate (required for booking creation)
#   - service_rate: Service rate amount
#   - status: "matched|not_found|rate_missing|error"
#   - source: "state|api" indicating where service_id came from
#
# The output is automatically available to downstream agent (booking_creation_agent)
# via Google ADK's SequentialAgent context passing mechanism.
service_agent = LlmAgent(
    name="service_agent",
    model=gemini_model(),
    description=SERVICE_AGENT_DESC,
    instruction=service_agent_instruction(CURRENT_DATE),
    tools=[ensure_service_matched],
    output_key="service_result"
)

__all__ = ["service_agent"]

