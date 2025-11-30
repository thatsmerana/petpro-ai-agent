import asyncio
import sys
import os
from typing import List, Dict
from dotenv import load_dotenv
import pytest
import uuid

# Add parent directory to path to allow imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# Google ADK imports
from google.genai import types

from petpro_agent.config import APP_NAME, session_service, get_runner

load_dotenv()


class PetSitterAgentTester:
    def __init__(self):
        self.session = None
        self.session_id = str(uuid.uuid4())  # Generate a unique session ID for this tester instance

    async def setup(self):
        """Async setup method to create session."""
        self.session = await session_service.create_session(
            app_name=APP_NAME,
            user_id="123e4567-e89b-12d3-a456-426614174001",
            session_id=self.session_id
        )

    async def cleanup(self):
        """Release resources to avoid unclosed aiohttp client session warnings."""
        # Wait for all pending tasks to complete (excluding current task)
        try:
            current_task = asyncio.current_task()
            # Get all pending tasks except the current one
            pending = [task for task in asyncio.all_tasks() 
                      if not task.done() and task is not current_task]
            if pending:
                # Wait for pending tasks with a timeout
                await asyncio.wait_for(asyncio.gather(*pending, return_exceptions=True), timeout=2.0)
        except (asyncio.TimeoutError, RuntimeError, AttributeError):
            # If timeout, event loop issues, or all_tasks not available, just continue
            pass
        
        # Small delay to ensure cleanup
        await asyncio.sleep(0.1)
        
        # Session service cleanup if available
        if session_service:
            close_method = getattr(session_service, "close", None)
            if callable(close_method):
                try:
                    result = close_method()
                    if asyncio.iscoroutine(result):
                        await result
                except Exception as e:
                    print(f"⚠️ SessionService close encountered: {e}")

    async def run_conversation(self, conversation: List[Dict[str, str]]):
        """Run agent with conversation messages."""
        runner = get_runner()
        for i, msg in enumerate(conversation):
            print(f"\n{'='*60}")
            print(f"Processing message {i+1}/{len(conversation)}: {msg['sender']}: {msg['message'][:50]}...")
            print(f"{'='*60}")
            
            user_query = (
                f"NEW MESSAGE: {msg['sender']}: {msg['message']}\n"
                "Analyze this new message within the ongoing pet sitting conversation and decide administrative actions."
            )
            content = types.Content(role='user', parts=[types.Part(text=user_query)])

            # Consume all events from the async generator to ensure all async operations complete
            events = []
            tool_calls_count = 0
            try:
                async for event in runner.run_async(
                    user_id="123e4567-e89b-12d3-a456-426614174001",
                    session_id=self.session_id,
                    new_message=content
                ):
                    events.append(event)
                    
                    # Inspect event structure for debugging
                    event_type = type(event).__name__
                    
                    # Check for tool calls - try multiple possible attributes
                    tool_calls = None
                    if hasattr(event, 'tool_calls'):
                        tool_calls = event.tool_calls
                    elif hasattr(event, 'tool_call'):
                        tool_calls = [event.tool_call] if event.tool_call else []
                    elif hasattr(event, 'function_calls'):
                        tool_calls = event.function_calls
                    
                    if tool_calls:
                        tool_calls_count += len(tool_calls) if isinstance(tool_calls, list) else 1
                        for tool_call in (tool_calls if isinstance(tool_calls, list) else [tool_calls]):
                            tool_name = getattr(tool_call, 'name', None) or getattr(tool_call, 'function_name', None) or str(tool_call)
                            print(f"🔧 TOOL CALLED: {tool_name} (event_type={event_type})")
                    
                    # Check for tool results
                    tool_results = None
                    if hasattr(event, 'tool_results'):
                        tool_results = event.tool_results
                    elif hasattr(event, 'tool_result'):
                        tool_results = [event.tool_result] if event.tool_result else []
                    elif hasattr(event, 'function_results'):
                        tool_results = event.function_results
                    
                    if tool_results:
                        for tool_result in (tool_results if isinstance(tool_results, list) else [tool_results]):
                            result_name = getattr(tool_result, 'name', None) or getattr(tool_result, 'function_name', None) or str(tool_result)
                            print(f"✅ TOOL RESULT: {result_name}")
                    
                    # Log agent responses
                    if event.is_final_response():
                        if hasattr(event, 'content') and event.content:
                            if hasattr(event.content, 'parts') and event.content.parts:
                                response_text = event.content.parts[0].text if hasattr(event.content.parts[0], 'text') else str(event.content.parts[0])
                                print(f"📝 Agent Response: {response_text[:200]}...")
                    
                    # Log agent name if available
                    if hasattr(event, 'agent_name'):
                        print(f"🤖 Agent: {event.agent_name}")
                
                print(f"📊 Summary: {len(events)} events, {tool_calls_count} tool calls")
                
            except Exception as e:
                print(f"❌ Error processing message: {e}")
                raise
            finally:
                # Ensure all async operations complete before moving to next message
                # Wait for any pending tasks related to this request
                try:
                    # Give time for any background HTTP requests to complete
                    await asyncio.sleep(0.5)
                    # Check for pending tasks and wait for them
                    current_task = asyncio.current_task()
                    pending = [task for task in asyncio.all_tasks() 
                              if not task.done() and task is not current_task]
                    if pending:
                        # Wait for pending tasks with a timeout
                        await asyncio.wait_for(
                            asyncio.gather(*pending, return_exceptions=True), 
                            timeout=3.0
                        )
                except (asyncio.TimeoutError, RuntimeError, AttributeError):
                    # If there are still pending tasks, give them more time
                    await asyncio.sleep(0.5)


SAMPLE_CONVERSATIONS = {  # Sample conversation scenarios
    "complete_booking": [
        {"sender": "System",
         "message": "Mike's pet professional id is ('123e4567-e89b-12d3-a456-426614174001'). Alice is our existing customer and Alice's customer id is ('123e4567-e89b-12d3-a456-426614174004')."},
        {"sender": "Alice",
         "message": "Hi Mike! I need someone to watch Bella and Max next weekend. Bella is my 3-year-old Golden Retriever and Max is a 1-year-old tabby cat."},
        {"sender": "Mike",
         "message": "My rate is $50/day for both pets. What times work for you?"},
        {"sender": "Alice",
         "message": "Perfect! I need you from 8 AM Saturday to 6 PM Sunday. So that's $100 total. My address is 123 Oak Street, and I can leave keys under the mat. Bella needs her medicine at 2 PM daily - it's in the kitchen cabinet."},
        {"sender": "Mike",
         "message": "Yes, I can do that weekend! I'll be there Saturday morning. Just to confirm - that's this coming Saturday the 23rd and Sunday the 24th, right?"},
        {"sender": "Alice", "message": "Yes exactly! Thanks Mike, you're the best. See you Saturday!"}
    ]
}

@pytest.fixture(scope="function")
async def agent_tester():
    """Fixture with function scope to ensure proper cleanup."""
    tester = PetSitterAgentTester()
    await tester.setup()
    try:
        yield tester
    finally:
        # Wait for any remaining async operations to complete
        try:
            await asyncio.sleep(0.3)
            current_task = asyncio.current_task()
            pending = [task for task in asyncio.all_tasks() 
                      if not task.done() and task is not current_task]
            if pending:
                await asyncio.wait_for(
                    asyncio.gather(*pending, return_exceptions=True), 
                    timeout=2.0
                )
        except (asyncio.TimeoutError, RuntimeError, AttributeError):
            pass
        finally:
            await tester.cleanup()

@pytest.mark.asyncio
async def test_complete_booking_scenario(agent_tester):
    """Test the complete booking conversation scenario."""
    conversation = SAMPLE_CONVERSATIONS["complete_booking"]
    await agent_tester.run_conversation(conversation)
    # Add assertions as needed (example: check session is not None)
    assert agent_tester.session is not None

@pytest.mark.asyncio
async def test_agent_initialization():
    tester = PetSitterAgentTester()
    await tester.setup()
    assert tester.session is not None
    assert get_runner() is not None
    await tester.cleanup()

async def main():
    print("🐕 Pet Sitter AI Agent - Test Program")
    print("=" * 50)
    print("Available test scenarios:")
    sitter_agent = PetSitterAgentTester()

    try:
        await sitter_agent.setup()

        for key in SAMPLE_CONVERSATIONS.keys():
            print(f"  - {key}")

        print("\n" + "=" * 50 + "\n")
        
        for scenario_name, conversation in SAMPLE_CONVERSATIONS.items():
            print(f"📋 Running scenario: {scenario_name}")
            await sitter_agent.run_conversation(conversation)
            print("\n" + "=" * 50 + "\n")
    finally:
        await sitter_agent.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
