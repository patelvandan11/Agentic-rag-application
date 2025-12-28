# agents/reasoning_agent.py
from agents import Agent

reasoning_agent = Agent(
    name="ReasoningAgent",
    instructions="""
    Compare multiple research approaches.
    Use ONLY provided context.
    Avoid hallucination.
    """
)
