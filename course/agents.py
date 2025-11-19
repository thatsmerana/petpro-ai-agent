from google.adk.agents import Agent
from google.adk.models.google_llm import Gemini
from google.adk.runners import InMemoryRunner
from google.adk.tools import google_search
from google.genai import types

print("✅ ADK components imported successfully.")

retry_config = types.HttpRetryOptions(
    attempts=5,
    exp_base=7,
    initial_delay=1,
    http_status_codes=[429, 500, 502, 503, 504]
)

root_agent = Agent(
    name="helpful_assistant",
    model=Gemini(
        model_name="gemini-2.5-flash-lite",
        retry_options=retry_config
    ),
    description="Helpful assistant that can answer questions using Google Search.",
    instruction="You are a helpful assistant that can use Google Search to find information.",
    tools=[google_search],
)

print("✅ Root Agent defined.")

runner = InMemoryRunner(agent=root_agent)

print("✅ Runner created.")

async def search():
    response = await runner.run_debug(
        "What are the latest advancements in renewable energy technologies?"
    )
    return response
