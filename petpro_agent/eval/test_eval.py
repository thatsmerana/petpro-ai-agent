import pytest
from google.adk.evaluation.agent_evaluator import AgentEvaluator
from google.adk.evaluation.eval_config import EvalConfig, BaseCriterion
import os
import json

@pytest.mark.asyncio
async def test_intent_classifier_agent_evaluation():
    """
    Runs the agent evaluation for the intent classifier agent.
    Tests that the agent correctly classifies intents including the new PET_SITTER_CONFIRMATION intent.
    
    Note: This evaluates the intent_classifier_agent in isolation. The agent outputs JSON with
    intent classification, which is then evaluated for correctness.
    
    Uses final_response_match_v2 for semantic equivalence checking, which is more flexible
    than exact string matching and better suited for JSON responses where structure may vary slightly.
    """
    # Load config file to get criteria
    config_path = os.path.join(os.path.dirname(__file__), "eval_config.json")
    with open(config_path, 'r') as f:
        config_data = json.load(f)
    
    # Create EvalConfig from the config file
    criteria_dict = {}
    for metric_name, threshold in config_data.get("criteria", {}).items():
        criteria_dict[metric_name] = BaseCriterion(threshold=threshold)
    
    eval_config = EvalConfig(criteria=criteria_dict)
    
    # Load EvalSet from JSON file
    from google.adk.evaluation.eval_set import EvalSet
    eval_set_path = os.path.join(os.path.dirname(__file__), "data", "intent_classifier_eval.test.json")
    with open(eval_set_path, 'r') as f:
        eval_set_data = json.load(f)
    eval_set = EvalSet(**eval_set_data)
    
    eval_results = await AgentEvaluator.evaluate_eval_set(
        agent_module="petpro_agent.sub_agents.intent_classifier_agent",
        eval_set=eval_set,
        eval_config=eval_config,
        num_runs=1,
        agent_name="intent_classifier_agent",
        print_detailed_results=True
    )
    return eval_results

@pytest.mark.asyncio
async def test_decision_maker_agent_evaluation():
    """
    Runs the agent evaluation for the decision maker agent.
    Tests that the agent correctly:
    - Collects information when intent is NOT PET_SITTER_CONFIRMATION
    - Executes workflow only when intent IS PET_SITTER_CONFIRMATION
    
    Note: This test may fail if APIs are not available, as the decision maker
    invokes booking_sequential_agent which makes API calls.
    
    Uses final_response_match_v2 for semantic equivalence checking, which is more flexible
    than exact string matching and better suited for JSON responses where structure may vary slightly.
    """
    # Create evaluation dataset for decision maker
    eval_dataset_path = os.path.join(os.path.dirname(__file__), "data", "decision_maker_eval.test.json")
    
    # Only run if dataset exists
    if os.path.exists(eval_dataset_path):
        # Load config file to get criteria
        config_path = os.path.join(os.path.dirname(__file__), "eval_config.json")
        with open(config_path, 'r') as f:
            config_data = json.load(f)
        
        # Create EvalConfig from the config file
        criteria_dict = {}
        for metric_name, threshold in config_data.get("criteria", {}).items():
            criteria_dict[metric_name] = BaseCriterion(threshold=threshold)
        
        eval_config = EvalConfig(criteria=criteria_dict)
        
        # Load EvalSet from JSON file
        from google.adk.evaluation.eval_set import EvalSet
        with open(eval_dataset_path, 'r') as f:
            eval_set_data = json.load(f)
        eval_set = EvalSet(**eval_set_data)
        
        eval_results = await AgentEvaluator.evaluate_eval_set(
            agent_module="petpro_agent.sub_agents.decision_maker_agent",
            eval_set=eval_set,
            eval_config=eval_config,
            num_runs=1,
            agent_name="decision_maker_agent",
            print_detailed_results=True
        )
        return eval_results
    else:
        pytest.skip(f"Decision maker evaluation dataset not found at {eval_dataset_path}")