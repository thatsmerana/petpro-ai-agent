from google.adk.agents import Agent, SequentialAgent, ParallelAgent, LoopAgent
from google.adk.models.google_llm import Gemini
from google.adk.runners import InMemoryRunner
from google.adk.tools import AgentTool, FunctionTool, google_search
from google.genai import types
import asyncio

print("✅ ADK components imported successfully.")

retry_config = types.HttpRetryOptions(
    attempts=3,
    exp_base=5,
    initial_delay=1,
    http_status_codes=[429, 500, 502, 503, 504]
)

# Define a research agent that uses google_search tool
research_agent = Agent(
    name="research_agent",
    model=Gemini(
        model="gemini-2.5-flash-lite",
        retry_options=retry_config
    ),
    instruction="""You are a research agent. Your only job is to use google_search tool to 
    find 2-3 relevant pieces of the information on the given topic and present 
    finding with proper citations.
    
    """,
    tools=[google_search],
    output_key="research_findings",
)

print("✅ research_agent created.")

# Define a summarization agent that summarizes research findings
summarization_agent = Agent(
    name="summarization_agent",
    model=Gemini(
        model="gemini-2.5-flash-lite",
        retry_options=retry_config
    ),
    instruction="""Read the research findings: {research_findings}
    Create a concise summary of the findings in 3-4 sentences.
    """,
    output_key="summary_report",
)

print("✅ summarizer_agent created.")

root_agent = Agent(
    name="ResearchCordinator",
    model=Gemini(
        model="gemini-2.5-flash-lite",
        retry_options=retry_config
    ),
    instruction="""
    You are a Research Coordinator Agent. 
    Your goal is to answer the user's query by orchestrating workflows.
    1. First, must call 'reserach_agent' to gather relevant information on the given users topic.
    2. Next, must call 'summarization_agent' to summarize the research findings.
    3. Finally, present the summary report to the user.
    """,
    tools=[AgentTool(research_agent), AgentTool(summarization_agent)],
)

print("✅ root_agent created.")

runner = InMemoryRunner(agent=root_agent)

print("✅ Runner created.")


async def search():
    response = await runner.run_debug(
        "What is MCP?"
    )
    return response
