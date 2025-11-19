import os
from dotenv import load_dotenv
from course import agents, multiagents, sequential_multiagents, parallel_multiagents
import asyncio

# Load environment variables from .env file
load_dotenv()

# Access the Gemini API key from environment variables
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if GOOGLE_API_KEY:
    print("Gemini API Key loaded successfully.")
else:
    print("Failed to load Gemini API Key.")

#
# response = asyncio.run(agents.search())
# print("Response from single agent:")
# print(response)

# response = asyncio.run(multiagents.search())
# print("Response from multiagent:")
# print(response)

# response = asyncio.run(sequential_multiagents.write())
# print("Response from sequential agent:")
# print(response)

# response = asyncio.run(parallel_multiagents.research("Run the daily executive briefing on Tech, Health, and Finance"))
# print("Response from parallel agent:")
# print(response)
