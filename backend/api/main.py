from fastapi import FastAPI
from agents import Runner
from ai_agents.planner_agent import planner_agent
from ai_agents.reasoning_agent import reasoning_agent
from ai_agents.summarizer_agent import summarizer_agent
from tools.search import search_papers

from dotenv import load_dotenv
load_dotenv()

app = FastAPI()

@app.post("/research")
async def research(query: str):
    # Step 1: Plan
    plan = await Runner.run(planner_agent, query)

    # Step 2: Search
    papers = search_papers(query)

    # Step 3: Reasoning
    context = "\n".join(p["summary"] for p in papers)
    reasoning_input = f"Question: {query}\nContext:\n{context}"

    reasoning = await Runner.run(reasoning_agent, reasoning_input)

    # Step 4: Summary
    summary = await Runner.run(summarizer_agent, reasoning.final_output)

    return {
        "query": query,
        "plan": plan.final_output,
        "papers": papers,
        "analysis": reasoning.final_output,
        "summary": summary.final_output
    }
