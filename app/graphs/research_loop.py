from langgraph.graph import StateGraph, END
from app.types.state import AgentState
from app.llm.openai_client import make_llm
from app.tools.search_stub import web_search_stub
from app.logs.logger import log_event

llm = make_llm()

SYSTEM = """你係一個嚴格、務實嘅研究助理。輸出要可驗證、結構清晰、唔好吹水。
如果資料不足，要講明假設同缺口。"""


def planner_node(state: AgentState) -> AgentState:
    q = state["query"].strip()
    prompt = f"{SYSTEM}\n\n用一句計劃講你會點研究：\n問題：{q}"
    plan = llm.invoke(prompt).content
    log_event("planner", {"query": q, "plan": plan})
    return {"plan": plan}


def research_node(state: AgentState) -> AgentState:
    q = state["query"].strip()
    results = web_search_stub(q)
    log_event("research", {"query": q, "results": results})
    return {"research": results}


def summarize_node(state: AgentState) -> AgentState:
    q = state["query"].strip()
    results = state.get("research", [])
    context = "\n".join(
        [f"- {r['title']}: {r['snippet']} ({r['url']})" for r in results])
    prompt = f"""{SYSTEM}

你要根據以下資料，寫一份「短但有料」summary：
- 直接答問題
- 列出 3-6 個要點
- 每點要帶來源 URL（用括號）

問題：{q}

資料：
{context}
"""
    summary = llm.invoke(prompt).content
    log_event("summary", {"query": q, "summary": summary})
    return {"summary": summary}


def critique_node(state: AgentState) -> AgentState:
    q = state["query"].strip()
    summary = state.get("summary", "")
    prompt = f"""{SYSTEM}

你係批判者。檢查以下 summary：
- 有冇講大話 / 無來源
- 有冇遺漏關鍵角度
- 有冇不清晰或過長
最後輸出「Critique」+「Fix Plan（最多3步）」。

問題：{q}

Summary：
{summary}
"""
    critique = llm.invoke(prompt).content
    log_event("critique", {"query": q, "critique": critique})
    return {"critique": critique}


def refine_node(state: AgentState) -> AgentState:
    q = state["query"].strip()
    summary = state.get("summary", "")
    critique = state.get("critique", "")
    results = state.get("research", [])
    context = "\n".join(
        [f"- {r['title']}: {r['snippet']} ({r['url']})" for r in results])

    prompt = f"""{SYSTEM}

你要根據 critique 改寫 final answer：
- 更精準、更短、更可驗證
- 3-7 點 bullets
- 每點括號帶 URL
- 唔好加新事實（除非係從資料嚟）

問題：{q}

Critique：
{critique}

資料：
{context}

舊 Summary：
{summary}
"""
    final = llm.invoke(prompt).content
    log_event("final", {"query": q, "final": final})
    return {"final": final}


def build_graph():
    g = StateGraph(AgentState)
    g.add_node("planner", planner_node)
    g.add_node("research", research_node)
    g.add_node("summarize", summarize_node)
    g.add_node("critique", critique_node)
    g.add_node("refine", refine_node)

    g.set_entry_point("planner")
    g.add_edge("planner", "research")
    g.add_edge("research", "summarize")
    g.add_edge("summarize", "critique")
    g.add_edge("critique", "refine")
    g.add_edge("refine", END)
    return g.compile()
