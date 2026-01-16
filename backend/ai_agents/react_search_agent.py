from agents import Agent
from langchain_openai import ChatOpenAI
from ai_agents.tools import (
    search_papers_tool,
    download_arxiv_tool,
    index_pdf_tool,
    
)

from tools.paper_search import search_database_tool

react_search_agent = Agent(
    name="ReActResearchAgent",
    model="gpt-4o-mini",
    instructions="""
You are a STRICT ReAct-style research agent.

You MUST internally follow:
Thought → Action → Observation → Thought → …

DO NOT reveal thoughts.
DO NOT explain reasoning.

Your goal:
- Find relevant research papers for the given query
- ONLY use arXiv papers
- Download papers
- Index them into the vector database

Allowed tools ONLY:
- search_papers_tool
- download_arxiv_tool
- index_pdf_tool

Rules:
1. ALWAYS start by calling search_papers_tool
2. ONLY process links containing "arxiv.org"
3. Use download_arxiv_tool to download PDFs
4. Index every downloaded PDF using index_pdf_tool
5. Skip failed downloads (no retries)
6. STOP after all valid papers are indexed

Forbidden:
- Using any other tools
- Asking questions
- Hallucinating papers
- Explaining reasoning

Final output MUST be a short summary only.

""",
    tools=[
        search_papers_tool,
        download_arxiv_tool,
        index_pdf_tool,
    ],
)
from agents import Agent

# react_existing_agent = Agent(
#     name="ReActExistingResearchAgent",
#     model="gpt-4o-mini",
#     instructions="""


# You MUST strictly follow this loop in order:
# Thought → Action → Observation → Thought → Final Answer

# Your goal:
# 1. Search the vector database for relevant research papers
# 2. Use the search results to answer the user's query

# Instructions:
# 1. Note answer like that "It seems I'm currently unable to retrieve relevant research papers or data on converting image patches into vector embeddings."

# """,
#     tools=[
#         search_database_tool,
#     ],
# )
