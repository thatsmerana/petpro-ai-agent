import os
from dotenv import load_dotenv
from google.adk.agents import LlmAgent, SequentialAgent

load_dotenv()

# Intent classified agent
intent_classifier_agent = LlmAgent(
    name="intent_classifier_agent",
    model="gemini-2.5-flash-lite",
    description="Classify pet sitting conversation intents and extract entities",
    instruction="""
   You are an intent classification agent for pet sitting group chat conversations.
    
    Analyze messages and classify them into these intents:
    - BOOKING_REQUEST: Customer asking for pet sitting services
    - SERVICE_CONFIRMATION: Pet sitter confirming availability/pricing  
    - BOOKING_DETAILS: Sharing specific booking details (times, address, instructions)
    - FINAL_CONFIRMATION: Both parties confirming the booking is complete
    - CASUAL_CONVERSATION: General chat, no administrative action needed
    
    Also extract any entities you can identify:
    - Customer information (name, address, phone, email)
    - Pet information (names, types, breeds, ages, special needs)
    - Booking details (dates, times, service type, pricing, location)
    
    Respond with JSON format:
    {
        "intent": "intent_name",
        "confidence": 0.95,
        "entities": {
            "customer": {...},
            "pets": [...],
            "booking": {...}
        },
        "should_execute": true/false
    }
    
    Set should_execute to true when confidence > 85% and sufficient information exists.
    """,
    output_key="intent_classification",
)

print("✅ Intent Classifier Agent defined.")

# Main orchestrator agent
root_agent = SequentialAgent(
    name="pet_sitting_orchestrator",
    description="AI assistant for pet sitting administrative tasks that monitors group chats and maintains conversation memory",
    sub_agents=[intent_classifier_agent],
)

print("✅ Root Agent defined.")

__all__ = ['root_agent']
