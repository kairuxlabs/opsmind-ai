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
    """You are the Critique Agent for OpsMind AI — an internal quality reviewer.
Your role is to critically evaluate the Decision Agent's recommendations BEFORE they reach the human.

You check for:
1. Consistency — do recommendations directly address the identified risks and insights?
2. Specificity — does each recommendation specify WHO does WHAT by WHEN?
3. Completeness — are all critical risks addressed by at least one recommendation?
4. Confidence calibration — is the stated confidence appropriate given the evidence?

Decision Agent Output:
- Recommendations: {recommendations}
- Confidence: {confidence}
- Explanation: {explanation}

Supporting Evidence:
- Insights: {insights}
- Risks: {risks}

Respond ONLY with valid JSON:
{{
  "consistency": true,
  "critique_passed": true,
  "adjusted_confidence": 0.89,
  "issues": [],
  "suggestions": [
    "Consider specifying a timeline for the resource allocation recommendation"
  ]
}}

Rules:
- critique_passed = true only if there are no critical issues (minor suggestions are OK)
- adjusted_confidence: start from the input confidence, add/subtract up to 0.10 based on evidence quality
- issues: list critical problems (unaddressed risks, vague ownership, contradictions)
- suggestions: list minor improvements that would strengthen the recommendations
- Keep issues and suggestions concise (under 15 words each)"""
)

chain = _prompt | _llm | JsonOutputParser()


async def critique_node(state: AgentState) -> dict:
    start = time.time()
    result = await chain.ainvoke({
        "recommendations": json.dumps(state.get("recommendations", []), indent=2),
        "confidence": state.get("confidence", 0.75),
        "explanation": json.dumps(state.get("explanation", []), indent=2),
        "insights": json.dumps(state.get("insights", {}), indent=2),
        "risks": json.dumps(state.get("risks", []), indent=2),
    })
    latency = int((time.time() - start) * 1000)

    critique = {
        "consistency": bool(result.get("consistency", True)),
        "critique_passed": bool(result.get("critique_passed", True)),
        "adjusted_confidence": float(result.get("adjusted_confidence", state.get("confidence", 0.75))),
        "issues": result.get("issues", []),
        "suggestions": result.get("suggestions", []),
    }

    log = {"agent": "critique", "latency_ms": latency, "output": critique}
    return {
        "critique": critique,
        "confidence": critique["adjusted_confidence"],
        "agent_logs": state.get("agent_logs", []) + [log],
    }
