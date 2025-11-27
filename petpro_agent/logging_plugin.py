"""
Logging plugin for PetPro AI Agent using Google ADK BasePlugin.

This plugin hooks into agent lifecycle callbacks to provide comprehensive
logging and observability for agent execution, model interactions, and tool calls.

Supports both standard logging and structured JSON logging for better observability
and integration with ADK Web UI and monitoring tools.
"""
import logging
import json
import time
from typing import Any, Dict, Optional

try:
    from google.adk.plugins.base_plugin import BasePlugin
    from google.adk.agents.callback_context import CallbackContext
    _BASE_PLUGIN_AVAILABLE = True
except ImportError:
    # Fallback for different ADK versions
    try:
        from google.adk.plugins import BasePlugin
        from google.adk.agents import CallbackContext
        _BASE_PLUGIN_AVAILABLE = True
    except ImportError:
        # If BasePlugin is not available, we'll create a minimal implementation
        BasePlugin = None
        CallbackContext = None
        _BASE_PLUGIN_AVAILABLE = False

logger = logging.getLogger(__name__)

if not _BASE_PLUGIN_AVAILABLE:
    logger.warning(
        "BasePlugin not available. Logging plugin may not function correctly. "
        "Please ensure google.adk.plugins.base_plugin is available."
    )


class AgentLoggingPlugin(BasePlugin if BasePlugin else object):
    """
    Logging plugin that captures agent lifecycle events for observability.
    
    This plugin logs:
    - Agent execution start/end with timing
    - Model requests and responses
    - Tool invocations and results
    - Errors and exceptions
    """
    
    def __init__(self, name: str = "AgentLoggingPlugin", use_json_logging: bool = False):
        """
        Initialize the logging plugin.
        
        Args:
            name: Plugin name
            use_json_logging: If True, logs will be in structured JSON format
                             for better parsing and ADK Web UI integration
        """
        if _BASE_PLUGIN_AVAILABLE and BasePlugin:
            super().__init__(name=name)
        else:
            self.name = name
            if not _BASE_PLUGIN_AVAILABLE:
                logger.warning(
                    f"{name} initialized but BasePlugin is not available. "
                    "Plugin callbacks may not be invoked by the ADK framework."
                )
        
        self.logger = logging.getLogger("petpro_agent.plugin")
        self.logger.setLevel(logging.DEBUG)
        self.use_json_logging = use_json_logging
        
        # Track execution times
        self._agent_start_times: Dict[str, float] = {}
        self._tool_start_times: Dict[str, float] = {}
        
        self.logger.info(f"Initialized {name} (JSON logging: {use_json_logging})")
    
    async def before_agent_callback(
        self, 
        callback_context: Optional[CallbackContext] = None,
        **kwargs
    ):
        """Called before an agent starts execution."""
        if callback_context:
            agent_name = getattr(callback_context, 'agent_name', 'unknown_agent')
            session_id = getattr(callback_context, 'session_id', 'unknown_session')
            user_id = getattr(callback_context, 'user_id', 'unknown_user')
        else:
            agent_name = kwargs.get('agent_name', 'unknown_agent')
            session_id = kwargs.get('session_id', 'unknown_session')
            user_id = kwargs.get('user_id', 'unknown_user')
        
        # Track start time
        start_key = f"{session_id}:{agent_name}"
        self._agent_start_times[start_key] = time.time()
        
        if self.use_json_logging:
            log_data = {
                "event": "agent_started",
                "agent_name": agent_name,
                "session_id": session_id,
                "user_id": user_id,
                "timestamp": time.time()
            }
            self.logger.info(json.dumps(log_data))
        else:
            self.logger.info(
                f"Agent execution started: agent={agent_name}, "
                f"session_id={session_id}, user_id={user_id}"
            )
        
        # Return None to allow execution to proceed
        return None
    
    async def after_agent_callback(
        self,
        callback_context: Optional[CallbackContext] = None,
        agent_output: Any = None,
        **kwargs
    ):
        """Called after an agent completes execution."""
        if callback_context:
            agent_name = getattr(callback_context, 'agent_name', 'unknown_agent')
            session_id = getattr(callback_context, 'session_id', 'unknown_session')
            user_id = getattr(callback_context, 'user_id', 'unknown_user')
        else:
            agent_name = kwargs.get('agent_name', 'unknown_agent')
            session_id = kwargs.get('session_id', 'unknown_session')
            user_id = kwargs.get('user_id', 'unknown_user')
        
        # Calculate execution time
        start_key = f"{session_id}:{agent_name}"
        start_time = self._agent_start_times.pop(start_key, None)
        execution_time = None
        if start_time:
            execution_time = time.time() - start_time
        
        # Log output summary
        output_summary = self._summarize_output(agent_output)
        
        if self.use_json_logging:
            log_data = {
                "event": "agent_completed",
                "agent_name": agent_name,
                "session_id": session_id,
                "user_id": user_id,
                "execution_time_seconds": round(execution_time, 3) if execution_time else None,
                "output_summary": output_summary,
                "timestamp": time.time()
            }
            self.logger.info(json.dumps(log_data))
        else:
            log_msg = (
                f"Agent execution completed: agent={agent_name}, "
                f"session_id={session_id}, user_id={user_id}"
            )
            if execution_time is not None:
                log_msg += f", execution_time={execution_time:.3f}s"
            if output_summary:
                log_msg += f", output={output_summary}"
            self.logger.info(log_msg)
        
        # Return the agent_output unchanged to allow it to proceed
        return agent_output
    
    async def before_model_callback(
        self,
        callback_context: Optional[CallbackContext] = None,
        llm_request: Any = None,
        **kwargs
    ):
        """Called before a model request is made."""
        if callback_context:
            agent_name = getattr(callback_context, 'agent_name', 'unknown_agent')
        else:
            agent_name = kwargs.get('agent_name', 'unknown_agent')
        
        # Extract request details
        request_info = self._extract_request_info(llm_request)
        
        if self.use_json_logging:
            log_data = {
                "event": "model_request",
                "agent_name": agent_name,
                "request_info": request_info,
                "timestamp": time.time()
            }
            self.logger.debug(json.dumps(log_data))
        else:
            self.logger.debug(
                f"Model request: agent={agent_name}, "
                f"request={request_info}"
            )
        
        # Return the request unchanged to allow it to proceed
        return llm_request
    
    async def after_model_callback(
        self,
        callback_context: Optional[CallbackContext] = None,
        llm_request: Any = None,
        llm_response: Any = None,
        **kwargs
    ):
        """Called after a model response is received."""
        if callback_context:
            agent_name = getattr(callback_context, 'agent_name', 'unknown_agent')
        else:
            agent_name = kwargs.get('agent_name', 'unknown_agent')
        
        # Extract response details
        response_info = self._extract_response_info(llm_response)
        request_info = self._extract_request_info(llm_request)
        
        if self.use_json_logging:
            log_data = {
                "event": "model_response",
                "agent_name": agent_name,
                "request_info": request_info,
                "response_info": response_info,
                "timestamp": time.time()
            }
            self.logger.debug(json.dumps(log_data))
        else:
            self.logger.debug(
                f"Model response: agent={agent_name}, "
                f"request={request_info}, response={response_info}"
            )
        
        # Return the response unchanged to allow it to proceed
        return llm_response
    
    async def before_tool_callback(
        self,
        callback_context: Optional[CallbackContext] = None,
        tool: Any = None,
        tool_args: Dict[str, Any] = None,
        **kwargs
    ):
        """Called before a tool is invoked."""
        if callback_context:
            agent_name = getattr(callback_context, 'agent_name', 'unknown_agent')
            session_id = getattr(callback_context, 'session_id', 'unknown_session')
        else:
            agent_name = kwargs.get('agent_name', 'unknown_agent')
            session_id = kwargs.get('session_id', 'unknown_session')
        
        tool_name = getattr(tool, 'name', 'unknown_tool') if tool else kwargs.get('tool_name', 'unknown_tool')
        tool_args = tool_args or kwargs.get('tool_args', {})
        
        # Track start time
        start_key = f"{session_id}:{tool_name}"
        self._tool_start_times[start_key] = time.time()
        
        # Sanitize tool args for logging (remove sensitive data)
        sanitized_args = self._sanitize_args(tool_args)
        
        if self.use_json_logging:
            log_data = {
                "event": "tool_started",
                "agent_name": agent_name,
                "session_id": session_id,
                "tool_name": tool_name,
                "tool_args": sanitized_args,
                "timestamp": time.time()
            }
            self.logger.info(json.dumps(log_data))
        else:
            self.logger.info(
                f"Tool invocation started: agent={agent_name}, "
                f"tool={tool_name}, args={sanitized_args}"
            )
        
        # Return tool_args unchanged to allow execution to proceed
        return tool_args
    
    async def after_tool_callback(
        self,
        callback_context: Optional[CallbackContext] = None,
        tool: Any = None,
        tool_args: Dict[str, Any] = None,
        tool_output: Any = None,
        **kwargs
    ):
        """Called after a tool completes execution."""
        if callback_context:
            agent_name = getattr(callback_context, 'agent_name', 'unknown_agent')
            session_id = getattr(callback_context, 'session_id', 'unknown_session')
        else:
            agent_name = kwargs.get('agent_name', 'unknown_agent')
            session_id = kwargs.get('session_id', 'unknown_session')
        
        tool_name = getattr(tool, 'name', 'unknown_tool') if tool else kwargs.get('tool_name', 'unknown_tool')
        tool_output = tool_output or kwargs.get('tool_output')
        
        # Calculate execution time
        start_key = f"{session_id}:{tool_name}"
        start_time = self._tool_start_times.pop(start_key, None)
        execution_time = None
        if start_time:
            execution_time = time.time() - start_time
        
        # Summarize output
        output_summary = self._summarize_output(tool_output)
        
        if self.use_json_logging:
            log_data = {
                "event": "tool_completed",
                "agent_name": agent_name,
                "session_id": session_id,
                "tool_name": tool_name,
                "execution_time_seconds": round(execution_time, 3) if execution_time else None,
                "output_summary": output_summary,
                "timestamp": time.time()
            }
            self.logger.info(json.dumps(log_data))
        else:
            log_msg = (
                f"Tool invocation completed: agent={agent_name}, "
                f"tool={tool_name}"
            )
            if execution_time is not None:
                log_msg += f", execution_time={execution_time:.3f}s"
            if output_summary:
                log_msg += f", output={output_summary}"
            self.logger.info(log_msg)
        
        # Return the tool_output unchanged to allow it to proceed
        return tool_output
    
    async def on_error_callback(
        self,
        callback_context: Optional[CallbackContext] = None,
        error: Exception = None,
        **kwargs
    ):
        """Called when an error occurs during agent execution."""
        if callback_context:
            agent_name = getattr(callback_context, 'agent_name', 'unknown_agent')
            session_id = getattr(callback_context, 'session_id', 'unknown_session')
        else:
            agent_name = kwargs.get('agent_name', 'unknown_agent')
            session_id = kwargs.get('session_id', 'unknown_session')
        
        error_type = type(error).__name__ if error else 'UnknownError'
        error_msg = str(error) if error else 'Unknown error'
        
        if self.use_json_logging:
            log_data = {
                "event": "error",
                "agent_name": agent_name,
                "session_id": session_id,
                "error_type": error_type,
                "error_message": error_msg,
                "timestamp": time.time()
            }
            # For JSON logging, include exception info as a separate field
            if error:
                import traceback
                log_data["traceback"] = traceback.format_exc()
            self.logger.error(json.dumps(log_data))
        else:
            self.logger.error(
                f"Error in agent execution: agent={agent_name}, "
                f"session_id={session_id}, error_type={error_type}, "
                f"error={error_msg}",
                exc_info=error
            )
    
    def _summarize_output(self, output: Any) -> str:
        """Create a summary string from agent/tool output."""
        if output is None:
            return None
        
        if isinstance(output, str):
            # Truncate long strings
            return output[:200] + "..." if len(output) > 200 else output
        elif isinstance(output, dict):
            # Summarize dictionary
            keys = list(output.keys())[:5]  # Show first 5 keys
            return f"dict(keys={keys}, ...)"
        else:
            return str(output)[:200]
    
    def _extract_request_info(self, request: Any) -> str:
        """Extract relevant information from LLM request."""
        if request is None:
            return "None"
        
        if hasattr(request, 'model'):
            return f"model={getattr(request, 'model', 'unknown')}"
        elif isinstance(request, dict):
            return f"dict(keys={list(request.keys())[:3]})"
        else:
            return str(type(request).__name__)
    
    def _extract_response_info(self, response: Any) -> str:
        """Extract relevant information from LLM response."""
        if response is None:
            return "None"
        
        if hasattr(response, 'text'):
            text = getattr(response, 'text', '')
            return f"text_length={len(text)}"
        elif isinstance(response, dict):
            return f"dict(keys={list(response.keys())[:3]})"
        else:
            return str(type(response).__name__)
    
    def _sanitize_args(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize tool arguments to remove sensitive data."""
        if not isinstance(args, dict):
            return args
        
        sanitized = {}
        sensitive_keys = ['password', 'token', 'api_key', 'secret', 'authorization']
        
        for key, value in args.items():
            if any(sensitive in key.lower() for sensitive in sensitive_keys):
                sanitized[key] = "***REDACTED***"
            elif isinstance(value, str) and len(value) > 100:
                sanitized[key] = value[:100] + "..."
            else:
                sanitized[key] = value
        
        return sanitized


# Create a singleton instance for easy import
# Set use_json_logging=True for structured JSON logs (better for ADK Web UI integration)
logging_plugin = AgentLoggingPlugin(use_json_logging=False)

__all__ = ["AgentLoggingPlugin", "logging_plugin"]

