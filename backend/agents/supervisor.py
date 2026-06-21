import time

from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from backend.config import settings
from backend.graph.state import AgentState

_llm = ChatOpenAI(
    model="deepseek-chat",
    api_key=settings.DEEPSEEK_API_KEY,
    base_url="https://api.deepseek.com",
    temperature=0.1,
)

_prompt = ChatPromptTemplate.from_template(
    """You are the Supervisor Agent for OpsMind AI — an Enterprise AI Operating System.
Analyze the user request and dynamically select which specialist agents are needed and in what order.

User Request: {user_query}

Respond ONLY with valid JSON (no markdown, no explanation):
{{
  "goal": "prepare_weekly_report",
  "route": ["planner", "knowledge", "analytics", "decision"]
}}

Available agents and when to include them:
- planner: Always include. Breaks the goal into concrete tasks.
- knowledge: Include when documents, data, or context retrieval is needed.
- analytics: Include when KPI analysis, risk detection, or pattern recognition is needed.
- decision: Always include last (before executor). Generates recommendations.

Route must always start with "planner" and end with "decision".
Goal should be a short snake_case phrase describing the primary objective."""
)

chain = _prompt | _llm | JsonOutputParser()


async def supervisor_node(state: AgentState) -> dict:
    start = time.time()
    result = await chain.ainvoke({"user_query": state["user_query"]})
    latency = int((time.time() - start) * 1000)
    log = {"agent": "supervisor", "latency_ms": latency, "output": result}
    return {
        "goal": result["goal"],
        "route": result.get("route", ["planner", "knowledge", "analytics", "decision"]),
        "status": "running",
        "agent_logs": state.get("agent_logs", []) + [log],
    }
