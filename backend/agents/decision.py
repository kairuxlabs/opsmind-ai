import json
import time

from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from backend.config import settings
from backend.graph.state import AgentState
from backend.memory.store import load_recent_feedback_for_goal

_llm = ChatOpenAI(
    model="deepseek-chat",
    api_key=settings.DEEPSEEK_API_KEY,
    base_url="https://api.deepseek.com",
    temperature=0.2,
)

_prompt = ChatPromptTemplate.from_template(
    """You are the Decision Agent for OpsMind AI — an Enterprise AI Operating System.
Based on the analytics results, generate 3-5 specific, actionable recommendations.
Each recommendation must include its own list of reasons (data points that justify it).
Include a confidence score (0.0-1.0) and an overall explanation summary.

User Query: {user_query}
Goal: {goal}
Insights: {insights}
Risks: {risks}
Past Feedback on Similar Goals: {feedback_context}

Respond ONLY with valid JSON:
{{
  "recommendations": [
    {{
      "text": "Allocate 2 additional engineers from DevOps team to Project Beta immediately to recover schedule",
      "reasons": [
        "Completion rate = 52% vs 75% target",
        "4-day delay pattern detected in last 2 sprints",
        "Resource shortage: 2 developers missing since May"
      ]
    }},
    {{
      "text": "Schedule scope review meeting with Project Gamma client by end of this week to lock requirements",
      "reasons": [
        "3 mid-sprint requirement changes recorded in Q2",
        "Scope instability is the primary blocker for delivery"
      ]
    }}
  ],
  "confidence": 0.87,
  "explanation": [
    "Project Beta completion rate is 52% vs 75% target — 4-day delay pattern detected",
    "Resource shortage is the primary driver: 2 developers missing since May",
    "Scope lock for Project Gamma will prevent recurring mid-sprint requirement changes"
  ]
}}

Rules:
- confidence between 0.0 and 1.0 (higher = more evidence supports the recommendations)
- Each recommendation must have 2-4 specific data-point reasons
- explanation is a 2-5 item overall summary across all recommendations
- Each recommendation text must specify WHO does WHAT by WHEN
- If past feedback shows "not_helpful", make recommendations MORE specific and evidence-based
- If past feedback shows "helpful", maintain the same style and depth"""
)

chain = _prompt | _llm | JsonOutputParser()


async def decision_node(state: AgentState) -> dict:
    start = time.time()

    # Load feedback from similar past goals to guide this recommendation
    try:
        past_feedback = await load_recent_feedback_for_goal(state.get("goal", ""), limit=5)
    except Exception:
        past_feedback = []

    if past_feedback:
        helpful_count = sum(1 for f in past_feedback if f.get("rating") == "helpful")
        feedback_context = (
            f"{helpful_count}/{len(past_feedback)} similar past recommendations were marked helpful. "
            + ("Users found these recommendations useful — maintain depth and specificity." if helpful_count > len(past_feedback) / 2
               else "Users found past recommendations not specific enough — be more concrete with owners and deadlines.")
        )
    else:
        feedback_context = "No prior feedback available for this goal type."

    result = await chain.ainvoke({
        "user_query": state["user_query"],
        "goal": state["goal"],
        "insights": json.dumps(state.get("insights", {})),
        "risks": json.dumps(state.get("risks", [])),
        "feedback_context": feedback_context,
    })
    latency = int((time.time() - start) * 1000)

    # Normalise: accept both legacy list[str] and new list[dict] from LLM
    raw_recs = result.get("recommendations", [])
    recommendations = [
        r if isinstance(r, dict) else {"text": r, "reasons": []}
        for r in raw_recs
    ]

    log = {"agent": "decision", "latency_ms": latency, "output": result}
    return {
        "recommendations": recommendations,
        "confidence": float(result.get("confidence", 0.75)),
        "explanation": result.get("explanation", []),
        "status": "waiting_approval",
        "agent_logs": state.get("agent_logs", []) + [log],
    }
