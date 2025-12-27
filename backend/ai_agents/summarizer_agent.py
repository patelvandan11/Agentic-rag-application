# agents/summarizer_agent.py
from agents import Agent

summarizer_agent = Agent(
    name="SummarizerAgent",
    instructions="""
    Generate a clear research summary.
    Use bullet points and short paragraphs.
    """
)
