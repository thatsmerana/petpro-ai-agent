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
            user_id="123e4567-e89b-12d3-a456-426614174001",
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

            async for event in self.runner.run_async(user_id="123e4567-e89b-12d3-a456-426614174001", session_id="test_session", new_message=content):
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
        {"sender": "Mike",
         "message": "My pet professional id is ('123e4567-e89b-12d3-a456-426614174001'). Alice is our existing customer and Alice's customer id is ('123e4567-e89b-12d3-a456-426614174004')."},
        {"sender": "Alice",
         "message": "Hi Mike! I need someone to watch Bella and Max next weekend. Bella is my 3-year-old Golden Retriever and Max is a 1-year-old tabby cat."},
        {"sender": "Mike",
         "message": "Yes, I can do that weekend. My rate is $50/day for both pets. What times work for you?"},
        {"sender": "Alice",
         "message": "Perfect! I need you from 8 AM Saturday to 6 PM Sunday. So that's $100 total. My address is 123 Oak Street, and I can leave keys under the mat. Bella needs her medicine at 2 PM daily - it's in the kitchen cabinet."},
        {"sender": "Mike",
         "message": "Sounds good! I'll be there Saturday morning. Just to confirm - that's this coming Saturday the 23rd and Sunday the 24th, right?"},
        {"sender": "Alice", "message": "Yes exactly! Thanks Mike, you're the best. See you Saturday!"}
    ],
    "new_customer_booking": [
        {"sender": "Mike",
         "message": "My pet professional id is ('123e4567-e89b-12d3-a456-426614174001')."},
        {"sender": "Jessica",
         "message": "Hi! I found your profile on PetPro. I'm Jessica Martinez and I'm new to the area. I need a pet sitter for my dog Charlie next week."},
        {"sender": "Mike",
         "message": "Welcome! I'd be happy to help. Tell me more about Charlie - what breed and age?"},
        {"sender": "Jessica",
         "message": "Charlie is a 5-year-old Labrador Retriever, very friendly and well-behaved. I need someone from December 1st to December 3rd while I'm away on a business trip."},
        {"sender": "Mike",
         "message": "Great! I charge $45 per day for one dog. That would be $135 for the three days. I can do morning and evening visits, or stay at your place if you prefer."},
        {"sender": "Jessica",
         "message": "Morning and evening visits would be perfect. My address is 456 Maple Avenue, Apt 2B. Charlie needs to be walked twice a day and fed at 7 AM and 6 PM. His food is in the pantry."},
        {"sender": "Mike",
         "message": "Perfect! Just to confirm - morning and evening visits from December 1st through December 3rd at 456 Maple Avenue, Apt 2B. Can you provide a contact number and email?"},
        {"sender": "Jessica",
         "message": "Sure! My phone is 555-123-4567 and email is jessica.martinez@email.com. I'll leave a key with the building manager."},
        {"sender": "Mike",
         "message": "Excellent! I'll send you a booking confirmation. Looking forward to meeting Charlie!"},
        {"sender": "Jessica", "message": "Thank you so much! I feel much better knowing Charlie will be in good hands."}
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
