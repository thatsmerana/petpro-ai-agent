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
        for msg in conversation:
            user_query = (
                f"NEW MESSAGE: {msg['sender']}: {msg['message']}\n"
                "Analyze this new message within the ongoing pet sitting conversation and decide administrative actions."
            )
            content = types.Content(role='user', parts=[types.Part(text=user_query)])

            async for event in get_runner().run_async(
                user_id="123e4567-e89b-12d3-a456-426614174001",
                session_id=self.session_id,
                new_message=content
            ):
                if event.is_final_response() and hasattr(event, 'content') and event.content and event.content.parts:
                    print(f"Agent Response: {event.content.parts[0].text}")


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

@pytest.fixture
async def agent_tester():
    tester = PetSitterAgentTester()
    await tester.setup()
    yield tester
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
