from dotenv import load_dotenv
from google.adk.agents import SequentialAgent

# Import sub-agents (each defined in its own file under sub_agents/)
from .sub_agents import intent_classifier_agent, decision_maker_agent

load_dotenv()

# Root orchestrator agent - entry point for continuous message processing
#
# EVENT LOOP PROCESSING:
# This SequentialAgent is designed to process messages in an event loop pattern:
# - Each new message from the conversation is processed sequentially
# - The agent maintains conversation memory through Google ADK's session management
# - Messages are processed in order: intent_classifier_agent → decision_maker_agent
# - The SequentialAgent ensures proper dependency chain and state preservation
#
# CONVERSATION MEMORY:
# The description explicitly mentions "maintains conversation memory" which is critical for:
# - Skip logic optimizations (checking history for existing customer_id, pet_ids, booking_id)
# - Context passing between conversation turns
# - Preventing redundant API calls for returning customers
#
# ARCHITECTURE:
# - Level 1: Intent Classification → Decision Making
# - Level 2: Decision Maker delegates to booking_sequential_agent (if needed)
# - Level 3: Booking Sequential Agent runs: customer → pet → booking (strict sequence)
#
# The SequentialAgent configuration is correct for event loop processing as it:
# 1. Processes sub-agents in strict sequence (intent → decision)
# 2. Maintains state between agent executions
# 3. Preserves conversation context for history checks
#
# Usage: See tests/test_agent.py for example event loop implementation using Runner
# with InMemorySessionService for continuous conversation processing.
root_agent = SequentialAgent(
    name="pet_sitting_orchestrator",
    description="AI assistant for pet sitting administrative tasks that monitors group chats and maintains conversation memory.",
    sub_agents=[intent_classifier_agent, decision_maker_agent],
)

print("✅ Root Agent defined (sub-agents loaded from sub_agents/).")

__all__ = ["root_agent"]
