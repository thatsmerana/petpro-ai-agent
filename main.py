"""
Main entry point for PetPro AI Agent.

This script runs the test agent to demonstrate the agent's capabilities
with sample conversations.
"""
import asyncio
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Access the Gemini API key from environment variables
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if GOOGLE_API_KEY:
    print("✅ Gemini API Key loaded successfully.")
else:
    print("❌ Failed to load Gemini API Key.")
    exit(1)

# Import and run the test agent
from petpro_agent.tests.test_agent import main

if __name__ == "__main__":
    asyncio.run(main())