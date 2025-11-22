from dotenv import load_dotenv
from google.adk.agents import SequentialAgent

# Import sub-agents (each defined in its own file under sub_agents/)
from .sub_agents import intent_classifier_agent, decision_maker_agent

load_dotenv()

# Root orchestrator agent only – other agents are defined in sub_agents modules
root_agent = SequentialAgent(
    name="pet_sitting_orchestrator",
    description="AI assistant for pet sitting administrative tasks that monitors group chats and maintains conversation memory.",
    sub_agents=[intent_classifier_agent, decision_maker_agent],
)

print("✅ Root Agent defined (sub-agents loaded from sub_agents/).")

__all__ = ["root_agent"]
