import json
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
    temperature=0.2,
)

_prompt = ChatPromptTemplate.from_template(
    """You are the Decision Agent for OpsMind AI.
Based on the analytics results, generate 3-5 specific, actionable recommendations.

User Query: {user_query}
Goal: {goal}
Insights: {insights}
Risks: {risks}

Respond ONLY with valid JSON:
{{
  "recommendations": [
    "Allocate 2 additional engineers from DevOps team to Project Beta immediately to recover schedule",
    "Schedule scope review meeting with Project Gamma client by end of this week to lock requirements",
    "Defer Project Epsilon Phase 2 to next sprint to reduce team overload from 95% to 80% capacity",
    "Conduct security audit pre-review on Project Gamma to prevent blocking next week's sprint"
  ]
}}

Each recommendation must be specific, actionable, and include WHO does WHAT by WHEN."""
)

chain = _prompt | _llm | JsonOutputParser()


async def decision_node(state: AgentState) -> dict:
    start = time.time()
    result = await chain.ainvoke({
        "user_query": state["user_query"],
        "goal": state["goal"],
        "insights": json.dumps(state.get("insights", {})),
        "risks": json.dumps(state.get("risks", [])),
    })
    latency = int((time.time() - start) * 1000)
    log = {"agent": "decision", "latency_ms": latency, "output": result}
    return {
        "recommendations": result.get("recommendations", []),
        "status": "waiting_approval",
        "agent_logs": state.get("agent_logs", []) + [log],
    }
