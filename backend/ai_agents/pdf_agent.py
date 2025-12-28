# agents/pdf_agent.py
from agents import Agent, Runner

pdf_agent = Agent(
    name="PDFAgent",
    instructions="""
    You extract key sections from research papers:
    abstract, method, dataset, results, limitations.
    """
)


