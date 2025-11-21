import os
from dotenv import load_dotenv
from google.adk.agents import LlmAgent, SequentialAgent

from .tools import get_customer_profile, create_customer, create_pet_profiles, create_booking, get_services

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

# Decision maker agent with tools and memory access
decision_maker_agent = LlmAgent(
    name="decision_maker_agent",
    model="gemini-2.5-flash-lite",
    description="Decide on pet sitting administrative actions based on classified intents and conversation memory",
    instruction="""
    You are the decision-making agent for a pet sitting administrative assistant.
    
    You will receive:
    1. Intent analysis from the previous agent: {intent_classification}
    2. Complete conversation context with accumulated information
    
    Based on the analysis and available information, decide what actions to take.
    
    Available tools:
    - get_customer_profile: Retrieve existing customer profiles from the database by passing the professional ID
    - create_customer: Create customer profiles when you have sufficient info for new customers
    - create_pet_profiles: Create pet profiles when you have pet details and customer_id
    - get_services: Retrieve available services and pricing for the pet sitter by passing the professional ID
    - create_booking: Create bookings when all details are confirmed

    Important: The professional ID is available in the session context as user_id. Use this ID when calling get_customer_profile and get_services.
    
    Decision criteria:
    - BOOKING_REQUEST (confidence <70%): Monitor only, don't act
    - SERVICE_CONFIRMATION (confidence 70-84%): Prepare data but wait
    - BOOKING_DETAILS (confidence 85-95%): Start creating customer/pet profiles
    - FINAL_CONFIRMATION (confidence >95%): Execute all necessary actions
    
    When should_execute is true, follow this sequence:
    1. Check if customer exists, create if needed
    2. Check if pets exist, create if needed using customer_id
    3. Obtain the latest customer_id and pet_ids by calling get_customer_profile.
    4. Create a booking only when all required details are available.
    
    Always explain your reasoning and list actions taken.
    """,
    output_key="administrative_decision",
    tools=[get_customer_profile, create_customer, create_pet_profiles, create_booking, get_services],
)

# Main orchestrator agent
root_agent = SequentialAgent(
    name="pet_sitting_orchestrator",
    description="AI assistant for pet sitting administrative tasks that monitors group chats and maintains conversation memory.",
    sub_agents=[intent_classifier_agent, decision_maker_agent],
)

print("✅ Root Agent defined.")

__all__ = ['root_agent']
