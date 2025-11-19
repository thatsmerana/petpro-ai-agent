from google.adk.agents import Agent, SequentialAgent
from google.adk.models.google_llm import Gemini
from google.adk.runners import InMemoryRunner
from google.genai import types
from google.adk.tools import AgentTool, FunctionTool, google_search

print("✅ ADK components imported successfully.")

retry_config = types.HttpRetryOptions(
    attempts=3,
    exp_base=5,
    initial_delay=1,
    http_status_codes=[429, 500, 502, 503, 504]
)

# Define Blog outline agent
outline_agent = Agent(
    name="OutlineAgent",
    model=Gemini(
        model="gemini-2.5-flash-lite",
        retry_options=retry_config
    ),
    instruction="""You are a blog outline agent. Your job is to create a detailed outline for a blog post on the given topic.
    The outline should include an introduction, main points with subpoints, and a conclusion.
    """,
    output_key="blog_outline",
)
print("✅ outline_agent created.")

# Define Blog writing agent
writing_agent = Agent(
    name="WritingAgent",
    model=Gemini(
        model="gemini-2.5-flash-lite",
        retry_options=retry_config
    ),
    instruction="""You are a blog writing agent.
    Using the provided outline: {blog_outline}, write a comprehensive 300-400 words blog post.
    Ensure the content is engaging, informative, and well-structured.
    """,
    output_key="blog_post",
)
print("✅ writing_agent created.")

# Define Agent to edit and polish the blog from the writer agent.
editing_agent = Agent(
    name="EditingAgent",
    model=Gemini(
        model="gemini-2.5-flash-lite",
        retry_options=retry_config
    ),
    instruction="""You are a blog editing agent.
    Review the blog post: {blog_post} for grammar, clarity, and coherence.
    Make necessary edits to enhance readability and overall quality.
    """,
    output_key="final_blog_post",
)
print("✅ editing_agent created.")

# Define the root agent that orchestrates the workflow
root_agent = SequentialAgent(
    name="BlogPostCoordinator",
    sub_agents=[outline_agent, writing_agent, editing_agent],
)

print("✅ root_agent created.")

runner = InMemoryRunner(agent=root_agent)

print("✅ Runner created.")

async def write():
    response = await runner.run_debug(
        "Create a blog post about the benefits of managing customer experience."
    )
    return response