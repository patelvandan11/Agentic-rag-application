# agents/search_agent.py
from agents import Agent

search_agent = Agent(
    name="SearchAgent",
    instructions="""
    You search for relevant research papers and articles.
    Return titles, sources, and short descriptions.
    """
)
