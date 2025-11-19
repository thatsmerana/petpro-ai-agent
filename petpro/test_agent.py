import asyncio
import json
import os
from typing import List, Dict
from dotenv import load_dotenv

# Google ADK imports
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from petpro import root_agent

load_dotenv()


class PetSitterAgentTester:
    def __init__(self):
        # Set up ADK Session service
        self.session_service = InMemorySessionService()
        self.session = None
        self.runner = None
        print("✅ PetSitterAgentTester initialized (awaiting setup).")

    async def setup(self):
        """Async setup method to create session and runner."""
        # Use the same app_name for both session and runner
        app_name = "pet_sitter_test_session"
        self.session = await self.session_service.create_session(
            app_name=app_name,
            user_id="test_user",
            session_id="test_session"
        )

        # Set up Runner with the same app_name
        self.runner = Runner(
            agent=root_agent,
            app_name=app_name,
            session_service=self.session_service
        )
        print("✅ Session and Runner created successfully.")

    async def process_conversation(self, conversation: List[Dict[str, str]]):

        for msg in conversation:
            user_query = f"""
            NEW MESSAGE: {msg['sender']}: {msg['message']}

            Analyze this new message in the context of the ongoing pet sitting conversation and decide what administrative actions to take.
            """

            content = types.Content(
                role='user',
                parts=[types.Part(text=user_query)]
            )

            print("\n💬 Processing conversation:")
            # run the agent and process events directly with async for
            final_response = None

            async for event in self.runner.run_async(user_id="test_user", session_id="test_session", new_message=content):
                if hasattr(event, 'content') and event.content and event.content.parts:
                    event_text = event.content.parts[0].text
                    if event.is_final_response():
                        final_response = event_text
                    else:
                        # Check if this contains JSON with entities
                        try:
                            event_data = json.loads(event_text)
                            if event_data.get("new_entities"):
                                print(f"📊 Extracted entities: {event_data['new_entities']}")
                        except:
                            pass

            if final_response:
                print(f"\n🎯 Agent Response: {final_response}")
            else:
                print(f"\n⚠️ No final response received")


# Sample conversation scenarios
SAMPLE_CONVERSATIONS = {
    "complete_booking": [
        {"sender": "Sarah",
         "message": "Hi Mike! I need someone to watch Bella and Max next weekend. Bella is my 3-year-old Golden Retriever and Max is a 1-year-old tabby cat."},
        {"sender": "Mike",
         "message": "Yes, I can do that weekend. My rate is $50/day for both pets. What times work for you?"},
        {"sender": "Sarah",
         "message": "Perfect! I need you from 8 AM Saturday to 6 PM Sunday. So that's $100 total. My address is 123 Oak Street, and I can leave keys under the mat. Bella needs her medicine at 2 PM daily - it's in the kitchen cabinet."},
        {"sender": "Mike",
         "message": "Sounds good! I'll be there Saturday morning. Just to confirm - that's this coming Saturday the 23rd and Sunday the 24th, right?"},
        {"sender": "Sarah", "message": "Yes exactly! Thanks Mike, you're the best. See you Saturday!"}
    ],

    "incomplete_booking": [
        {"sender": "Jennifer", "message": "Hey Alex, do you do dog walking?"},
        {"sender": "Alex", "message": "Yes I do! What kind of dog and how often?"},
        {"sender": "Jennifer", "message": "I have a German Shepherd named Rex. Maybe 2-3 times a week?"},
        {"sender": "Alex", "message": "I charge $25 per walk. Does that work?"},
        {"sender": "Jennifer", "message": "That sounds reasonable. Let me think about it and get back to you."}
    ],

    "complex_booking": [
        {"sender": "David",
         "message": "Hi Lisa! My wife and I are going out of town for a week. Can you watch our pets?"},
        {"sender": "Lisa", "message": "Sure! Tell me about your pets and the dates."},
        {"sender": "David",
         "message": "We have 3 cats - Mittens (2 years), Shadow (4 years), and Whiskers (6 years). Also a small parrot named Kiwi. We'll be gone July 15th to 22nd."},
        {"sender": "Lisa",
         "message": "I can do that. For that many pets for a week, I'd charge $60/day. That's $420 total."},
        {"sender": "David",
         "message": "That works. We live at 456 Pine Avenue. Kiwi needs fresh fruit daily and the cats have automatic feeders. I'll leave detailed instructions."},
        {"sender": "Lisa",
         "message": "Perfect! I'll stop by the day before to meet everyone and get the instructions."},
        {"sender": "David", "message": "Excellent! Looking forward to working with you."}
    ]
}

async def main():
    print("🐕 Pet Sitter AI Agent - Test Program")
    print("=" * 50)
    print("Available test scenarios:")
    sitter_agent = PetSitterAgentTester()

    await sitter_agent.setup()

    for key in SAMPLE_CONVERSATIONS.keys():
        print(f"  - {key}")

    for scenario_name, conversation in SAMPLE_CONVERSATIONS.items():
        print(f"  - {scenario_name}")

        await sitter_agent.process_conversation(conversation)
        print("\n" + "=" * 50 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
