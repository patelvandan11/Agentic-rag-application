from agents import Agent, Runner

planner_agent = Agent(
    name="PlannerAgent",
    instructions="""
    You are a planning agent.
    Break the research query into clear, ordered steps.
    Do NOT answer the question.
    Output numbered steps only.
    """
)
