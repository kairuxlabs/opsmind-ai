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
Analyze the user request and dynamically select ONLY the specialist agents truly needed, in the right order.

User Request: {user_query}

Respond ONLY with valid JSON (no markdown, no explanation):
{{
  "goal": "prepare_weekly_report",
  "route": ["planner", "knowledge", "analytics", "decision"]
}}

Available agents:
- planner: Include for complex multi-step tasks that need decomposition (reports, audits, planning).
- knowledge: Include when documents, historical data, or context retrieval is needed.
- analytics: Include when KPI computation, anomaly detection, or risk analysis is needed.
- decision: ALWAYS include — generates final recommendations and confidence score.

Routing examples (choose the minimal set that fits the request):
- "Prepare weekly report"         → ["planner", "knowledge", "analytics", "decision"]
- "Analyze project risks"         → ["knowledge", "analytics", "decision"]
- "What do we know about X?"      → ["knowledge", "decision"]
- "Give me a quick recommendation"→ ["decision"]

Rules:
- decision must always be last.
- Only include planner for tasks that explicitly need step-by-step decomposition.
- Only include knowledge when retrieval is needed.
- Only include analytics when quantitative analysis or risk scoring is needed.
- Goal should be a short snake_case phrase describing the primary objective."""
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
