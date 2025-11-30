"""
Utility functions for context extraction and validation in the PetPro Agent system.

These utilities help extract customer_id, pet_ids, and booking_id from conversation
history and agent outputs to support skip logic optimizations.
"""

import json
import re
from typing import Optional, List, Dict, Any

try:
    from google.adk.runners import Runner
    from google.adk.sessions import SessionService
except ImportError:
    Runner = None
    SessionService = None


def parse_agent_output_json(output_text: str) -> Optional[Dict[str, Any]]:
    """
    Safely parse JSON from agent output text.
    
    Handles cases where output is not pure JSON (e.g., text + JSON, markdown code blocks).
    Attempts to extract JSON from the text using multiple strategies.
    
    Args:
        output_text: The raw output text from an agent, which may contain JSON
        
    Returns:
        Parsed JSON as a dictionary, or None if parsing fails
    """
    if not output_text:
        return None
    
    # Strategy 1: Try parsing the entire text as JSON
    try:
        return json.loads(output_text.strip())
    except (json.JSONDecodeError, ValueError):
        pass
    
    # Strategy 2: Extract JSON from markdown code blocks (```json ... ```)
    json_block_pattern = r'```(?:json)?\s*(\{.*?\})\s*```'
    matches = re.findall(json_block_pattern, output_text, re.DOTALL)
    if matches:
        try:
            return json.loads(matches[0])
        except (json.JSONDecodeError, ValueError):
            pass
    
    # Strategy 3: Find JSON object in text (look for {...})
    json_object_pattern = r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}'
    matches = re.findall(json_object_pattern, output_text, re.DOTALL)
    for match in matches:
        try:
            parsed = json.loads(match)
            if isinstance(parsed, dict):
                return parsed
        except (json.JSONDecodeError, ValueError):
            continue
    
    # Strategy 4: Try parsing lines that look like JSON
    for line in output_text.split('\n'):
        line = line.strip()
        if line.startswith('{') and line.endswith('}'):
            try:
                return json.loads(line)
            except (json.JSONDecodeError, ValueError):
                continue
    
    return None


def extract_customer_id_from_context(context: Dict[str, Any]) -> Optional[str]:
    """
    Extract customer_id from conversation context/agent outputs.
    
    Searches in the following order:
    1. decision_maker_agent output (administrative_decision) - customer_id field
    2. customer_agent output (customer_result) - customer_id field
    3. booking_sequential_agent output - customer_id field
    4. booking_creation_agent output (booking_result) - customer_id field
    
    Args:
        context: Dictionary containing agent outputs and conversation history
                 Expected keys: administrative_decision, customer_result, booking_result
        
    Returns:
        customer_id as string if found, None otherwise
    """
    if not context:
        return None
    
    # Check decision_maker_agent output
    admin_decision = context.get("administrative_decision")
    if admin_decision:
        if isinstance(admin_decision, str):
            parsed = parse_agent_output_json(admin_decision)
            if parsed and parsed.get("customer_id"):
                return parsed["customer_id"]
        elif isinstance(admin_decision, dict) and admin_decision.get("customer_id"):
            return admin_decision["customer_id"]
    
    # Check customer_agent output
    customer_result = context.get("customer_result")
    if customer_result:
        if isinstance(customer_result, str):
            parsed = parse_agent_output_json(customer_result)
            if parsed and parsed.get("customer_id"):
                return parsed["customer_id"]
        elif isinstance(customer_result, dict) and customer_result.get("customer_id"):
            return customer_result["customer_id"]
    
    # Check booking_creation_agent output (may contain customer_id)
    booking_result = context.get("booking_result")
    if booking_result:
        if isinstance(booking_result, str):
            parsed = parse_agent_output_json(booking_result)
            if parsed and parsed.get("customer_id"):
                return parsed["customer_id"]
        elif isinstance(booking_result, dict) and booking_result.get("customer_id"):
            return booking_result["customer_id"]
    
    return None


def extract_pet_ids_from_context(context: Dict[str, Any]) -> Optional[List[str]]:
    """
    Extract pet_ids array from conversation context/agent outputs.
    
    Searches in the following order:
    1. decision_maker_agent output (administrative_decision) - pet_ids field
    2. pet_agent output (pet_result) - pet_ids field
    3. booking_creation_agent output (booking_result) - pet_ids field
    
    Args:
        context: Dictionary containing agent outputs and conversation history
                 Expected keys: administrative_decision, pet_result, booking_result
        
    Returns:
        List of pet_ids if found, None otherwise
    """
    if not context:
        return None
    
    # Check decision_maker_agent output
    admin_decision = context.get("administrative_decision")
    if admin_decision:
        if isinstance(admin_decision, str):
            parsed = parse_agent_output_json(admin_decision)
            if parsed and parsed.get("pet_ids"):
                pet_ids = parsed["pet_ids"]
                if isinstance(pet_ids, list):
                    return pet_ids
        elif isinstance(admin_decision, dict) and admin_decision.get("pet_ids"):
            pet_ids = admin_decision["pet_ids"]
            if isinstance(pet_ids, list):
                return pet_ids
    
    # Check pet_agent output
    pet_result = context.get("pet_result")
    if pet_result:
        if isinstance(pet_result, str):
            parsed = parse_agent_output_json(pet_result)
            if parsed and parsed.get("pet_ids"):
                pet_ids = parsed["pet_ids"]
                if isinstance(pet_ids, list):
                    return pet_ids
        elif isinstance(pet_result, dict) and pet_result.get("pet_ids"):
            pet_ids = pet_result["pet_ids"]
            if isinstance(pet_ids, list):
                return pet_ids
    
    # Check booking_creation_agent output (may contain pet_ids)
    booking_result = context.get("booking_result")
    if booking_result:
        if isinstance(booking_result, str):
            parsed = parse_agent_output_json(booking_result)
            if parsed and parsed.get("pet_ids"):
                pet_ids = parsed["pet_ids"]
                if isinstance(pet_ids, list):
                    return pet_ids
        elif isinstance(booking_result, dict) and booking_result.get("pet_ids"):
            pet_ids = booking_result["pet_ids"]
            if isinstance(pet_ids, list):
                return pet_ids
    
    return None


def extract_booking_id_from_context(context: Dict[str, Any]) -> Optional[str]:
    """
    Extract booking_id from conversation context/agent outputs.
    
    Searches in the following order:
    1. decision_maker_agent output (administrative_decision) - booking_id field
    2. booking_creation_agent output (booking_result) - booking_id field
    3. booking_creation_agent output (booking_result) - existing_booking_id field
    
    Args:
        context: Dictionary containing agent outputs and conversation history
                 Expected keys: administrative_decision, booking_result
        
    Returns:
        booking_id as string if found, None otherwise
    """
    if not context:
        return None
    
    # Check decision_maker_agent output
    admin_decision = context.get("administrative_decision")
    if admin_decision:
        if isinstance(admin_decision, str):
            parsed = parse_agent_output_json(admin_decision)
            if parsed and parsed.get("booking_id"):
                return parsed["booking_id"]
        elif isinstance(admin_decision, dict) and admin_decision.get("booking_id"):
            return admin_decision["booking_id"]
    
    # Check booking_creation_agent output
    booking_result = context.get("booking_result")
    if booking_result:
        if isinstance(booking_result, str):
            parsed = parse_agent_output_json(booking_result)
            if parsed:
                # Try booking_id first, then existing_booking_id
                booking_id = parsed.get("booking_id") or parsed.get("existing_booking_id")
                if booking_id:
                    return booking_id
        elif isinstance(booking_result, dict):
            booking_id = booking_result.get("booking_id") or booking_result.get("existing_booking_id")
            if booking_id:
                return booking_id
    
    return None


def validate_agent_output(output_key: str, output_text: str, expected_fields: List[str]) -> bool:
    """
    Validate that agent output contains properly structured JSON with expected fields.
    
    Args:
        output_key: The output key name (e.g., "customer_result", "pet_result")
        output_text: The raw output text from the agent
        expected_fields: List of field names that should be present in the JSON
        
    Returns:
        True if output is valid (contains all expected fields), False otherwise
    """
    if not output_text:
        print(f"⚠️ Warning: {output_key} output is empty")
        return False
    
    parsed = parse_agent_output_json(output_text)
    if not parsed:
        print(f"⚠️ Warning: {output_key} output is not valid JSON")
        return False
    
    missing_fields = [field for field in expected_fields if field not in parsed]
    if missing_fields:
        print(f"⚠️ Warning: {output_key} output missing fields: {missing_fields}")
        return False
    
    return True


def create_runner_with_logging(
    app=None,
    agent=None,
    app_name: str = None,
    session_service: SessionService = None,
    enable_logging: bool = True
) -> Optional[Runner]:
    """
    Create a Runner instance with logging plugin enabled.
    
    This helper function creates a Runner with the logging plugin automatically
    registered for observability. The logging plugin will capture agent lifecycle
    events, model interactions, and tool calls.
    
    Supports both App-based (new) and agent-based (legacy) Runner creation.
    
    Args:
        app: App instance (new style, preferred)
        agent: The agent instance to run (legacy style, used if app is None)
        app_name: Application name for the runner (legacy style, used if app is None)
        session_service: Session service instance
        enable_logging: Whether to enable logging plugin (default: True)
        
    Returns:
        Runner instance with logging plugin registered, or None if Runner is not available
    """
    if Runner is None:
        return None
    
    try:
        from .logging_plugin import logging_plugin
        
        plugins = [logging_plugin] if enable_logging else []
        
        # Try to create runner with plugins parameter
        try:
            if app is not None:
                # New style: use App
                runner = Runner(
                    app=app,
                    session_service=session_service,
                    plugins=plugins
                )
            else:
                # Legacy style: use agent and app_name
                runner = Runner(
                    agent=agent,
                    app_name=app_name,
                    session_service=session_service,
                    plugins=plugins
                )
            return runner
        except TypeError:
            # If plugins parameter not supported, create runner and register plugin
            if app is not None:
                runner = Runner(
                    app=app,
                    session_service=session_service
                )
            else:
                runner = Runner(
                    agent=agent,
                    app_name=app_name,
                    session_service=session_service
                )
            
            if enable_logging:
                # Try different methods to register plugin
                if hasattr(runner, 'register_plugin'):
                    runner.register_plugin(logging_plugin)
                elif hasattr(runner, 'add_plugin'):
                    runner.add_plugin(logging_plugin)
                elif hasattr(runner, 'plugins'):
                    if not hasattr(runner.plugins, 'append'):
                        runner.plugins = [logging_plugin]
                    else:
                        runner.plugins.append(logging_plugin)
            
            return runner
    except ImportError:
        # If logging plugin not available, create runner without it
        if app is not None:
            return Runner(
                app=app,
                session_service=session_service
            )
        else:
            return Runner(
                agent=agent,
                app_name=app_name,
                session_service=session_service
            )


__all__ = [
    "parse_agent_output_json",
    "extract_customer_id_from_context",
    "extract_pet_ids_from_context",
    "extract_booking_id_from_context",
    "validate_agent_output",
    "create_runner_with_logging",
]

