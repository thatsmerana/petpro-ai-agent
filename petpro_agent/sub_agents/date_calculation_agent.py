"""
Date calculation agent using BuiltInCodeExecutor for dynamic date parsing.

This module creates a specialized agent for date calculations that uses BuiltInCodeExecutor.
The agent is part of the booking_sequential_agent workflow and calculates dates
from natural language phrases, storing results in state for the booking_creation_agent.
"""
from google.adk.agents import LlmAgent
from google.adk.code_executors import BuiltInCodeExecutor
from ..prompts import DATE_CALCULATION_AGENT_DESC, date_calculation_agent_instruction
from ..config import gemini_model, CURRENT_DATE

# Create a specialized agent for date calculations using BuiltInCodeExecutor
# This agent can generate and execute Python code dynamically to parse natural
# language date phrases into structured date/time information.
# It's part of the booking_sequential_agent sequence: customer → pet → service → date → booking
date_calculation_agent = LlmAgent(
    model=gemini_model(),
    name="date_calculation_agent",
    description=DATE_CALCULATION_AGENT_DESC,
    instruction=date_calculation_agent_instruction(CURRENT_DATE),
    code_executor=BuiltInCodeExecutor(),
    output_key="date_result"  # Output key for passing results to booking_creation_agent
)

__all__ = ["date_calculation_agent"]

