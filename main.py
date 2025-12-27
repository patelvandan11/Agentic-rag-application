import asyncio
from agents import Agent, Runner
from tools import add_numbers, multiply_numbers
from dotenv import load_dotenv
load_dotenv()
import streamlit as st

root_agent = Agent(
    name="Function Tools Agent",
    instructions="""
    
    SYSTEM RULES (STRICT):
    - You are NOT allowed to answer using your own knowledge.
    - You MUST use a tool to answer.
    - If the question cannot be answered using the available tools,
      respond EXACTLY with:
      "I am unable to answer that question."

    Available tools:
    - add_numbers
    - multiply_numbers

    Allowed questions:
    - Addition
    - Multiplication

    Forbidden:
    - Definitions
    - Explanations
    - General knowledge
    - AI/ML questions

    Output:
    - Only final numeric result OR the refusal message.
    """,
    tools=[add_numbers, multiply_numbers],
)


async def main():
    
    query=input("Enter your query: ")
    result = await Runner.run(
        root_agent,
        query
    )
    print(result.final_output)

if __name__ == "__main__":
    asyncio.run(main())
