from google.adk.agents import SequentialAgent
from .customer_agent import customer_agent
from .pet_agent import pet_agent
from .booking_creation_agent import booking_creation_agent

# Define the booking sequential agent -- orchestrates customer, pet, and booking creation agents in sequence.
#
# CONTEXT PASSING MECHANISM:
# Google ADK's SequentialAgent automatically passes context between sub-agents via output_keys:
# - customer_agent output (output_key="customer_result") is automatically available to pet_agent
# - pet_agent output (output_key="pet_result") is automatically available to booking_creation_agent
# - All previous agent outputs are accessible in conversation history for each subsequent agent
#
# This enables the skip logic optimizations:
# - customer_agent can check decision_maker_agent output for customer_verified flag
# - pet_agent can check customer_agent output for existing pets and customer_id
# - booking_creation_agent can check decision_maker_agent output for booking_id
# - Each agent can access the full conversation history to find verification state
#
# STRICT SEQUENTIAL EXECUTION:
# The SequentialAgent enforces strict sequential execution to protect database integrity:
# 1. customer_agent MUST complete before pet_agent starts (ensures customer_id exists)
# 2. pet_agent MUST complete before booking_creation_agent starts (ensures pet_ids exist)
# 3. This dependency chain prevents orphaned records and ensures data consistency
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
    description="Execute complete booking workflow: customer → pets → booking creation in sequence with shared state",
    sub_agents=[customer_agent, pet_agent, booking_creation_agent]
)

__all__ = ["booking_sequential_agent"]

