from google.adk.agents import Agent, ParallelAgent, SequentialAgent
from google.adk.models.google_llm import Gemini
from google.adk.runners import InMemoryRunner
from google.genai import types
from google.adk.tools import AgentTool, FunctionTool, google_search
import asyncio

print("✅ ADK components imported successfully.")

retry_config = types.HttpRetryOptions(
    attempts=3,
    exp_base=5,
    initial_delay=1,
    http_status_codes=[429, 500, 502, 503, 504]
)

# Tech research agent : uses google_search tool to gather information on technology topics
tech_research_agent = Agent(
    name="tech_research_agent",
    model=Gemini(
        model="gemini-2.5-flash-lite",
        retry_options=retry_config
    ),
    instruction="""You are a tech research agent. Your only job is to use google_search tool to 
    find 2-3 relevant pieces of the information on the given technology topic and present 
    finding with proper citations.
    
    """,
    tools=[google_search],
    output_key="tech_research_findings",
)

# Health research agent : uses google_search tool to gather information on health topics
health_research_agent = Agent(
    name="health_research_agent",
    model=Gemini(
        model="gemini-2.5-flash-lite",
        retry_options=retry_config
    ),
    instruction="""You are a health research agent. Your only job is to use google_search tool to 
    find 2-3 relevant pieces of the information on the given health topic and present 
    finding with proper citations.
    """,
    tools=[google_search],
    output_key="health_research_findings",
)

# Finance research agent : uses google_search tool to gather information on finance topics
finance_research_agent = Agent(
    name="finance_research_agent",
    model=Gemini(
        model="gemini-2.5-flash-lite",
        retry_options=retry_config
    ),
    instruction="""You are a finance research agent. Your only job is to use google_search tool to 
    find 2-3 relevant pieces of the information on the given finance topic and present 
    finding with proper citations.
    """,
    tools=[google_search],
    output_key="finance_research_findings",
)

# Aggregator agent to compile findings from all research agents
aggregator_agent = Agent(
    name="aggregator_agent",
    model=Gemini(
        model="gemini-2.5-flash-lite",
        retry_options=retry_config
    ),
    instruction="""You are an aggregator agent.
    Compile the findings from the following research agents:
    Technology Findings: {tech_research_findings}
    Health Findings: {health_research_findings}
    Finance Findings: {finance_research_findings}
    Create a comprehensive report summarizing the key points from each domain.
    """,
    output_key="comprehensive_report",
)

parallel_research_team = ParallelAgent(
    name="MultiDomainResearchCoordinator",
    sub_agents=[
        tech_research_agent,
        health_research_agent,
        finance_research_agent
    ],
)

root_agent = SequentialAgent(
    name="OverallResearchCoordinator",
    sub_agents=[
        parallel_research_team,
        aggregator_agent
    ],
)

runner = InMemoryRunner(agent=root_agent)


async def research(query: str):
    response = await runner.run_debug(query)
    return response