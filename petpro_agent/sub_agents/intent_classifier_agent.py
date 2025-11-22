from ..prompts import INTENT_CLASSIFIER_DESC, intent_classifier_instruction
from ..config import CURRENT_DATE, gemini_model
from google.adk.agents import LlmAgent

# Define the intent classifier agent -- responsible for classifying user intents.
intent_classifier_agent = LlmAgent(
    name="intent_classifier_agent",
    model=gemini_model(),
    description=INTENT_CLASSIFIER_DESC,
    instruction=intent_classifier_instruction(CURRENT_DATE),
    output_key="intent_classification",
)

__all__ = ["intent_classifier_agent"]

