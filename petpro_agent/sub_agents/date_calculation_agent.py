"""
Date calculation agent using BuiltInCodeExecutor for dynamic date parsing.

This module creates a specialized agent for date calculations that uses BuiltInCodeExecutor.
According to Google ADK documentation, BuiltInCodeExecutor should be used as the
`code_executor` parameter on a separate agent, which is then wrapped in AgentTool
and added to the parent agent's tools list.

This allows the booking_creation_agent to have both code execution capability
AND other tools (get_bookings, create_booking, etc.) by delegating date calculations
to this specialized agent.
"""
from google.adk.agents import LlmAgent
from google.adk.code_executors import BuiltInCodeExecutor
from ..prompts import DATE_CALCULATION_AGENT_DESC, date_calculation_agent_instruction
from ..config import gemini_model, CURRENT_DATE

# Create a specialized agent for date calculations using BuiltInCodeExecutor
# This agent can generate and execute Python code dynamically to parse natural
# language date phrases into structured date/time information.
date_calculation_agent = LlmAgent(
    model=gemini_model(),
    name="date_calculation_agent",
    description=DATE_CALCULATION_AGENT_DESC,
    instruction=date_calculation_agent_instruction(CURRENT_DATE),
    code_executor=BuiltInCodeExecutor()
)

__all__ = ["date_calculation_agent"]

