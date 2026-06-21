import time

from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from backend.config import settings
from backend.graph.state import AgentState
from backend.services.tracing import get_tracer_config

_llm = ChatOpenAI(
    model="deepseek-chat",
    api_key=settings.DEEPSEEK_API_KEY,
    base_url="https://api.deepseek.com",
    temperature=0.1,
)

_prompt = ChatPromptTemplate.from_template(
    """You are the Planner Agent for OpsMind AI.
Break down the goal into 4-6 concrete, ordered tasks.

Goal: {goal}
User Request: {user_query}

Respond ONLY with valid JSON:
{{
  "tasks": [
    "collect_project_status_data",
    "analyze_performance_metrics",
    "identify_risks_and_blockers",
    "generate_recommendations",
    "create_weekly_report"
  ]
}}

Tasks must be specific, actionable, snake_case, ordered logically."""
)

chain = _prompt | _llm | JsonOutputParser()


async def planner_node(state: AgentState) -> dict:
    start = time.time()
    result = await chain.ainvoke({
        "goal": state["goal"],
        "user_query": state["user_query"],
    }, config=get_tracer_config("planner"))
    latency = int((time.time() - start) * 1000)
    log = {"agent": "planner", "latency_ms": latency, "output": result}
    return {
        "tasks": result["tasks"],
        "agent_logs": state.get("agent_logs", []) + [log],
    }
