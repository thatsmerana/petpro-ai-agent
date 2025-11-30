# petpro-ai-agent

Custom AI Agent built using Google ADK to automate administrative tasks for Pet Professionals

## Overview

PetPro AI Agent is an intelligent multi-agent system that automates administrative tasks for pet sitting businesses. The system monitors group chat conversations between customers and pet sitters, intelligently extracts booking information from natural language, and automatically manages customer profiles, pet profiles, and bookings in a pet professionals database.

### Key Concepts

- **Multi-Agent Architecture**: Hierarchical system with specialized agents for intent classification, decision making, and workflow execution
- **Intent Classification**: Classifies 6 different conversation intents (booking request, booking details, pet sitter confirmation, service confirmation, final confirmation, casual conversation)
- **Confirmation-Based Execution**: Two-phase approach—information collection phase stores booking details, execution phase only triggers when pet sitter confirms availability
- **Skip Logic Optimization**: Checks conversation history before API calls, skipping redundant operations for returning customers (50-70% reduction in API calls)
- **Update vs Create Intelligence**: Detects existing bookings in conversation history, prioritizes update path when booking_id exists
- **Conversation Memory**: Maintains state across multiple message turns, tracks customer_id, pet_ids, booking_id for context-aware decision making
- **Context Compaction**: Events compaction configuration manages conversation history efficiently, reducing token usage while maintaining context

## Technology Stack

- **Framework**: Google ADK (Agent Development Kit)
- **LLM**: Google Gemini 2.5 Flash Lite
- **Language**: Python 3.10+
- **Architecture**: Multi-agent system with sequential workflow orchestration
- **Session Management**: InMemorySessionService for conversation state
- **Code Execution**: BuiltInCodeExecutor for dynamic date calculations
- **Observability**: Custom logging plugin with agent lifecycle tracking
- **Testing**: pytest with async support for integration and evaluation tests
- **HTTP Client**: aiohttp for async API calls
- **Date Parsing**: dateparser and python-dateutil for natural language date processing
- **Fuzzy Matching**: rapidfuzz for semantic service matching

## Project Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/thatsmerana/petpro-ai-agent.git
   cd petpro-ai-agent
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**
   
   Create a `.env` file in the project root directory with the following variables:
   ```bash
   # Required: Google Gemini API Key for LLM access
   GOOGLE_API_KEY=your_google_api_key_here
   
   # Required: Pet Professionals API Configuration
   PET_PROFESSIONALS_API_BASE_URL=https://api.example.com
   PET_PROFESSIONALS_API_KEY=your_api_key_here
   ```
   
   **Environment Variables:**
   - `GOOGLE_API_KEY` (Required): Your Google Gemini API key for LLM model access
   - `PET_PROFESSIONALS_API_BASE_URL` (Required): Base URL for the Pet Professionals REST API
   - `PET_PROFESSIONALS_API_KEY` (Required): API key for authenticating with the Pet Professionals API

5. **Run the application:**
   ```bash
   python main.py
   ```

## Testing

The project includes comprehensive testing with both integration tests and evaluation tests.

### Running Tests

**Run all tests:**
```bash
pytest
```

**Run tests with verbose output:**
```bash
pytest -v
```

**Run specific test file:**
```bash
# Integration tests
pytest petpro_agent/tests/test_agent.py

# Evaluation tests
pytest petpro_agent/eval/test_eval.py
```

**Run specific test function:**
```bash
pytest petpro_agent/tests/test_agent.py::test_complete_booking_scenario
pytest petpro_agent/eval/test_eval.py::test_intent_classifier_agent_evaluation
```

**Run tests with coverage (requires pytest-cov):**
```bash
# Install pytest-cov first (already included in requirements.txt)
pip install pytest-cov

# Run tests with coverage report
pytest --cov=petpro_agent --cov-report=html

# View coverage report (opens in browser)
# Open htmlcov/index.html in your browser
```

### Test Types

1. **Integration Tests** (`petpro_agent/tests/test_agent.py`):
   - Test complete agent workflows with sample conversations
   - Verify agent initialization and session management
   - Test booking creation scenarios end-to-end

2. **Evaluation Tests** (`petpro_agent/eval/test_eval.py`):
   - Use Google ADK's `AgentEvaluator` to measure agent performance
   - Test intent classifier accuracy with `intent_classifier_eval.test.json`
   - Test decision maker correctness with `decision_maker_eval.test.json`
   - Evaluate agent responses against expected outputs using semantic matching

### Test Configuration

- **pytest.ini**: Configures async mode for pytest-asyncio
- **eval_config.json**: Defines evaluation criteria and thresholds for agent evaluation
- **Test Data**: Located in `petpro_agent/eval/data/` directory

### Test Requirements

- All tests require the `GOOGLE_API_KEY` environment variable to be set
- Integration tests may require `PET_PROFESSIONALS_API_BASE_URL` and `PET_PROFESSIONALS_API_KEY` if testing full API integration
- Tests use async/await patterns and require `pytest-asyncio` plugin
