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

react_existing_agent = Agent(
    name="ReActExistingResearchAgent",
    model="gpt-4o-mini",
    instructions="""
YYou are a ReAct-style agent.

You MUST strictly follow this loop in order:
Thought → Action → Observation → Thought → Final Answer

Rules:
- Every response must start with a Thought
- Thoughts describe your reasoning and next step
- Actions must call an allowed tool
- Observations must only contain tool outputs
- Repeat the loop until the answer is found
- End with a Final Answer ONLY when the task is complete

Constraints:
- Do NOT skip any step
- Do NOT combine steps
- Do NOT produce a Final Answer without at least one Action
- Do NOT hallucinate information
- If information is unavailable, state it clearly in the Final Answer

""",
    tools=[
        search_database_tool,
    ],
)
