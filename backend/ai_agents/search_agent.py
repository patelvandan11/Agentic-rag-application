# agents/search_agent.py
from agents import Agent

search_agent = Agent(
    name="SearchAgent",
    instructions="""
    You search for relevant research papers and articles.
    Return titles, sources, and short descriptions.
    """
)

from tools.paper_search import search_research_papers
from tools.paper_search import search_database_tool

react_existing_agent = Agent(
    name="ReActExistingResearchAgent",
    model="gpt-4o-mini",
    instructions="""
You are a ReAct-style research agent.

You MUST strictly follow this reasoning loop internally:
Thought → Action → Observation → Thought → Action → Observation → ... → Final Answer

Goal:
- Search for relevant research papers using the existing database
- Perform MULTIPLE searches if required to fully answer the query
- Refine your search queries step-by-step if results are insufficient

Rules:
- Use ONLY search_database_tool
- DO NOT download papers
- DO NOT index papers
- DO NOT hallucinate papers
- Base answers ONLY on tool observations

Final Answer:
- Provide a concise summary of all relevant papers found
- Mention how many searches were performed
""",
    tools=[search_database_tool],
)
