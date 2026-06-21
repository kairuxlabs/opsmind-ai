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
    """You are the Analytics Agent for OpsMind AI — an Enterprise AI Operating System.
Analyze the context data: extract KPIs, detect anomalies, identify risks, and compute an enterprise health score.

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
  }},
  "health_score": 72
}}

Health Score formula (0-100):
- Start at 100
- Subtract 10 for each Critical risk, 5 for each High risk
- Subtract 5 for each project with completion_rate below 70%
- Add 5 if team velocity >= 90% of target
- Clamp result between 0 and 100"""
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
        "health_score": int(result.get("health_score", 70)),
        "agent_logs": state.get("agent_logs", []) + [log],
    }
