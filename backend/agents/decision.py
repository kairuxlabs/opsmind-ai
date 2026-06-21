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
    """You are the Decision Agent for OpsMind AI — an Enterprise AI Operating System.
Based on the analytics results, generate 3-5 specific, actionable recommendations.
Include a confidence score (0.0-1.0) reflecting how certain you are given the evidence.
Explain your reasoning so humans can validate or override your decision.

User Query: {user_query}
Goal: {goal}
Insights: {insights}
Risks: {risks}

Respond ONLY with valid JSON:
{{
  "recommendations": [
    "Allocate 2 additional engineers from DevOps team to Project Beta immediately to recover schedule",
    "Schedule scope review meeting with Project Gamma client by end of this week to lock requirements"
  ],
  "confidence": 0.87,
  "explanation": [
    "Project Beta completion rate is 52% vs 75% target — 4-day delay pattern detected",
    "Resource shortage is the primary driver: 2 developers missing since May",
    "Scope lock for Project Gamma will prevent the recurring mid-sprint requirement changes"
  ]
}}

Rules:
- confidence between 0.0 and 1.0 (higher = more evidence supports the recommendation)
- explanation must list 2-5 specific data points that drove the decision
- Each recommendation must specify WHO does WHAT by WHEN"""
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
        "confidence": float(result.get("confidence", 0.75)),
        "explanation": result.get("explanation", []),
        "status": "waiting_approval",
        "agent_logs": state.get("agent_logs", []) + [log],
    }
