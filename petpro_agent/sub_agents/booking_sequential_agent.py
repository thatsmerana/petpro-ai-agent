from google.adk.agents import SequentialAgent
from .customer_agent import customer_agent
from .pet_agent import pet_agent
from .service_agent import service_agent
from .date_calculation_agent import date_calculation_agent
from .booking_creation_agent import booking_creation_agent

# Define the booking sequential agent -- orchestrates customer, pet, service, date calculation, and booking creation agents in sequence.
#
# CONTEXT PASSING MECHANISM:
# Google ADK's SequentialAgent automatically passes context between sub-agents via output_keys:
# - customer_agent output (output_key="customer_result") is automatically available to pet_agent
# - pet_agent output (output_key="pet_result") is automatically available to service_agent
# - service_agent output (output_key="service_result") is automatically available to date_calculation_agent
# - date_calculation_agent output (output_key="date_result") is automatically available to booking_creation_agent
# - All previous agent outputs are accessible in conversation history for each subsequent agent
#
# This enables the skip logic optimizations:
# - customer_agent can check decision_maker_agent output for customer_verified flag
# - pet_agent can check customer_agent output for existing pets and customer_id
# - service_agent can match service and validate service rate exists
# - date_calculation_agent calculates dates from natural language phrases
# - booking_creation_agent can check decision_maker_agent output for booking_id
# - Each agent can access the full conversation history to find verification state
#
# STRICT SEQUENTIAL EXECUTION:
# The SequentialAgent enforces strict sequential execution to protect database integrity:
# 1. customer_agent MUST complete before pet_agent starts (ensures customer_id exists)
# 2. pet_agent MUST complete before service_agent starts (ensures pet_ids exist)
# 3. service_agent MUST complete before date_calculation_agent starts (ensures service_id and service_rate_id exist)
# 4. date_calculation_agent MUST complete before booking_creation_agent starts (ensures dates are calculated)
# 5. This dependency chain prevents orphaned records and ensures data consistency
#
# SHARED STATE:
# The description mentions "shared state" which refers to:
# - Conversation context accessible to all sub-agents
# - Output from previous agents in the sequence
# - Verification flags from decision_maker_agent
# - Session state maintained by Google ADK's session management
#
# The SequentialAgent ensures that state is properly shared while maintaining execution order.
booking_sequential_agent = SequentialAgent(
    name="booking_sequential_agent",
    description="Execute complete booking workflow: customer → pets → service → date calculation → booking creation in sequence with shared state. MUST run all five agents: customer_agent, pet_agent, service_agent, date_calculation_agent, and booking_creation_agent. The final response MUST come from booking_creation_agent.",
    sub_agents=[customer_agent, pet_agent, service_agent, date_calculation_agent, booking_creation_agent]
)

agent = booking_sequential_agent

__all__ = ["booking_sequential_agent"]

