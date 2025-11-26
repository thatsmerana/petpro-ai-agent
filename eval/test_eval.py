import pytest
from google.adk.evaluation.agent_evaluator import AgentEvaluator
import os

@pytest.mark.asyncio
async def test_intent_classifier_agent_evaluation():
    """
    Runs the agent evaluation for the intent classifier agent.
    """
    eval_results = await AgentEvaluator.evaluate(
        agent_module="petpro_agent.sub_agents.intent_classifier_agent",
        eval_dataset_file_path_or_dir=os.path.join(os.path.dirname(__file__), "data", "intent_classifier_eval.test.json")
    )