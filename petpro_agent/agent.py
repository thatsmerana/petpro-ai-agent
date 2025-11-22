from dotenv import load_dotenv
from google.adk.agents import LlmAgent, SequentialAgent
import datetime

from google.adk.models import Gemini
from google.genai import types
from .tools import get_customer_profile, create_customer, create_pet_profiles, create_booking, get_services, get_bookings, update_booking
from .prompts import (
    INTENT_CLASSIFIER_DESC,
    CUSTOMER_AGENT_DESC,
    PET_AGENT_DESC,
    BOOKING_CREATION_DESC,
    DECISION_MAKER_DESC,
    intent_classifier_instruction,
    customer_agent_instruction,
    pet_agent_instruction,
    booking_creation_agent_instruction,
    decision_maker_instruction,
)

load_dotenv()

# Current date reused for all instruction builders
_current_date = datetime.datetime.now().strftime("%Y-%m-%d")

# HTTP retry configuration for Gemini model (robust against transient 429/5xx)
retry_config = types.HttpRetryOptions(
    attempts=5,
    exp_base=7,
    initial_delay=1,
    http_status_codes=[429, 500, 503, 504],
)

print("✅ Retry configuration set.")

# Intent classified agent
intent_classifier_agent = LlmAgent(
    name="intent_classifier_agent",
    model=Gemini(model="gemini-2.5-flash-lite", retry_options=retry_config),
    description=INTENT_CLASSIFIER_DESC,
    instruction=intent_classifier_instruction(_current_date),
    output_key="intent_classification",
)

print("✅ Intent Classifier Agent defined.")

# Customer Management Agent
customer_agent = LlmAgent(
    name="customer_agent",
    model=Gemini(model="gemini-2.5-flash-lite", retry_options=retry_config),
    description=CUSTOMER_AGENT_DESC,
    instruction=customer_agent_instruction(_current_date),
    tools=[get_customer_profile, create_customer],
    output_key="customer_result"
)

# Pet Management Agent
pet_agent = LlmAgent(
    name="pet_agent",
    model=Gemini(model="gemini-2.5-flash-lite", retry_options=retry_config),
    description=PET_AGENT_DESC,
    instruction=pet_agent_instruction(_current_date),
    tools=[create_pet_profiles],
    output_key="pet_result"
)

# Booking Creation Agent
booking_creation_agent = LlmAgent(
    name="booking_creation_agent",
    model=Gemini(model="gemini-2.5-flash-lite", retry_options=retry_config),
    description=BOOKING_CREATION_DESC,
    instruction=booking_creation_agent_instruction(_current_date),
    tools=[get_bookings, get_services, create_booking, update_booking],
    output_key="booking_result"
)

# Booking Sequential Agent - orchestrates the sequential workflow with shared state
booking_agent = SequentialAgent(
    name="booking_sequential_agent",
    description="Execute complete booking workflow: customer → pets → booking creation in sequence with shared state",
    sub_agents=[customer_agent, pet_agent, booking_creation_agent]
)

print("✅ Booking Sequential Agent with sub-agents defined.")

# Decision maker agent - delegates to booking_agent
decision_maker_agent = LlmAgent(
    name="decision_maker_agent",
    model=Gemini(model="gemini-2.5-flash-lite", retry_options=retry_config),
    description=DECISION_MAKER_DESC,
    instruction=decision_maker_instruction(_current_date),
    output_key="administrative_decision",
    sub_agents=[booking_agent]
)

print("✅ Decision Maker Agent defined.")

# Main orchestrator agent
root_agent = SequentialAgent(
    name="pet_sitting_orchestrator",
    description="AI assistant for pet sitting administrative tasks that monitors group chats and maintains conversation memory.",
    sub_agents=[intent_classifier_agent, decision_maker_agent],
)

print("✅ Root Agent defined.")

__all__ = ['root_agent']
