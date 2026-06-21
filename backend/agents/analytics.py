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
    temperature=0.1,
)

_prompt = ChatPromptTemplate.from_template(
    """You are the Analytics Agent for OpsMind AI.
Analyze the context data and extract KPIs, identify risks, and provide insights.

User Query: {user_query}
Tasks: {tasks}
Retrieved Context:
{documents}

Respond ONLY with valid JSON:
{{
  "kpis": {{
    "total_projects": 5,
    "on_track": 3,
    "at_risk": 2,
    "completion_rate": "60%",
    "team_velocity": "42/50 story points"
  }},
  "risks": [
    {{"project": "Project Beta", "risk_level": "High", "reason": "Missing 2 developers since May"}},
    {{"project": "Project Gamma", "risk_level": "Critical", "reason": "Client requirements changed mid-sprint"}}
  ],
  "insights": {{
    "summary": "Team is operating below velocity target with 2 projects at risk",
    "key_finding": "Resource constraints are the primary driver of project delays"
  }}
}}"""
)

chain = _prompt | _llm | JsonOutputParser()


async def analytics_node(state: AgentState) -> dict:
    start = time.time()
    docs_text = "\n".join(d["content"] for d in state.get("documents", [])[:5])
    result = await chain.ainvoke({
        "user_query": state["user_query"],
        "tasks": json.dumps(state.get("tasks", [])),
        "documents": docs_text or "No documents retrieved. Use general knowledge for analysis.",
    })
    latency = int((time.time() - start) * 1000)
    log = {"agent": "analytics", "latency_ms": latency, "output": result}
    return {
        "insights": result.get("insights", {}),
        "risks": result.get("risks", []),
        "agent_logs": state.get("agent_logs", []) + [log],
    }
