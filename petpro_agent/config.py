# Shared configuration for agent modules
import logging
import logging.handlers
import os
import datetime
import json
from pathlib import Path
from google.genai import types
from google.adk.models import Gemini
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService

# Import App and EventsCompactionConfig for context compaction
try:
    from google.adk.apps.app import App, EventsCompactionConfig
    _APP_AVAILABLE = True
except ImportError:
    # Fallback for older ADK versions
    try:
        from google.adk.apps import App, EventsCompactionConfig
        _APP_AVAILABLE = True
    except ImportError:
        App = None
        EventsCompactionConfig = None
        _APP_AVAILABLE = False
        import logging
        logging.warning("App and EventsCompactionConfig not available. Context compaction will be disabled.")

# Create logs directory if it doesn't exist
logs_dir = Path("logs")
logs_dir.mkdir(exist_ok=True)

# Clean up any previous logs in logs directory (optional - comment out if you want to keep logs)
# for log_file in ["logger.log", "web.log", "tunnel.log"]:
#     log_path = logs_dir / log_file
#     if log_path.exists():
#         log_path.unlink()
#         print(f"🧹 Cleaned up {log_path}")

# Configure logging with DEBUG log level and log rotation
# Log rotation: max 10MB per file, keep 5 backup files
log_file_path = logs_dir / "logger.log"
log_handler = logging.handlers.RotatingFileHandler(
    filename=str(log_file_path),
    maxBytes=10 * 1024 * 1024,  # 10MB
    backupCount=5,
    encoding='utf-8'
)

# Use structured format that's easy to parse
log_formatter = logging.Formatter(
    "%(asctime)s|%(filename)s:%(lineno)s|%(levelname)s|%(name)s|%(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
log_handler.setFormatter(log_formatter)

# Configure root logger
root_logger = logging.getLogger()
root_logger.setLevel(logging.DEBUG)
root_logger.addHandler(log_handler)

# Also add console handler for development (optional)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(log_formatter)
root_logger.addHandler(console_handler)

print("✅ Logging configured with rotation (10MB, 5 backups)")

# Current date (ISO) used in prompt builders
CURRENT_DATE = datetime.datetime.now().strftime("%Y-%m-%d")

# Retry configuration to mitigate transient rate limit / server errors
RETRY_CONFIG = types.HttpRetryOptions(
    attempts=5,
    exp_base=7,
    initial_delay=1,
    http_status_codes=[429, 500, 503, 504],
)

def gemini_model(name: str = "gemini-2.5-flash-lite"):
    """Return a Gemini model instance with shared retry options."""
    return Gemini(model=name, retry_options=RETRY_CONFIG)

# Application name for ADK Runner and Session
APP_NAME = "pet_sitter_agent"

# Initialize session service (singleton)
session_service = InMemorySessionService()

# Initialize app with context compaction (singleton, lazy initialization to avoid circular imports)
def get_app():
    """Get or create the App instance with events compaction enabled."""
    if not hasattr(get_app, '_app'):
        from . import root_agent
        
        if _APP_AVAILABLE and App and EventsCompactionConfig:
            # Configure events compaction: compact after every 5 conversations
            compaction_config = EventsCompactionConfig(
                compaction_interval=5,  # Trigger compaction every 5 conversations
                overlap_size=1,  # Keep 1 previous turn for context
            )
            
            app = App(
                name=APP_NAME,
                root_agent=root_agent,
                events_compaction_config=compaction_config,
            )
            print("✅ App created with Events Compaction enabled (interval=5, overlap=1)")
        else:
            # Fallback: create App without compaction if not available
            if App:
                app = App(
                    name=APP_NAME,
                    root_agent=root_agent,
                )
                print("⚠️ App created without Events Compaction (EventsCompactionConfig not available)")
            else:
                app = None
                print("⚠️ App class not available, will use Runner directly")
        
        get_app._app = app
    
    return get_app._app

# Initialize runner (singleton, lazy initialization to avoid circular imports)
def get_runner():
    """Get or create the Runner instance with logging plugin and context compaction."""
    if not hasattr(get_runner, '_runner'):
        from .utils import create_runner_with_logging
        
        app = get_app()
        
        if app is not None:
            # Use App-based Runner with compaction
            runner = create_runner_with_logging(
                app=app,
                session_service=session_service,
                enable_logging=True
            )
            
            # Fallback to standard Runner with app
            if runner is None:
                runner = Runner(
                    app=app,
                    session_service=session_service
                )
        else:
            # Fallback to old-style Runner (if App not available)
            from . import root_agent
            runner = create_runner_with_logging(
                agent=root_agent,
                app_name=APP_NAME,
                session_service=session_service,
                enable_logging=True
            )
            
            if runner is None:
                runner = Runner(
                    agent=root_agent,
                    app_name=APP_NAME,
                    session_service=session_service
                )
        
        get_runner._runner = runner
    
    return get_runner._runner

__all__ = [
    "CURRENT_DATE", 
    "RETRY_CONFIG", 
    "gemini_model",
    "APP_NAME",
    "session_service",
    "get_app",
    "get_runner"
]

