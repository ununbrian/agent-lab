from langgraph.graph import StateGraph, END
from app.types.state import AgentState
from app.llm.openai_client import make_llm
from app.tools.tavily_search import tavily_search
from app.tools.source_quality import split_by_quality
from app.logs.logger import log_event
from app.tools.evidence_check import has_enough_evidence
from app.memory.qdrant_store import MemoryStore
memory = MemoryStore()
llm = make_llm()

SYSTEM = """你係一個嚴格、務實嘅研究助理。輸出要可驗證、結構清晰、唔好吹水。
如果資料不足，要講明假設同缺口。"""


def memory_search_node(state: AgentState) -> AgentState:
    q = state["query"].strip()
    hits = memory.search(q, top_k=1)

    if hits:
        best = hits[0]
        ans = (best.get("answer") or "").strip()
        if ans:   # ⭐ 只有有答案先當 memory_hit
            return {
                "memory_hit": True,
                "memory_answer": ans,
                "memory_sources": best.get("sources", []),
            }

    return {"memory_hit": False}



def memory_answer_node(state: AgentState) -> AgentState:
    ans = state.get("memory_answer", "").strip()
    sources = state.get("memory_sources", [])

    if not ans:
        return {}

    if sources:
        refs = "\n".join([f"- {u}" for u in sources])
        final = f"{ans}\n\n---\n\n(from memory)\n{refs}"
    else:
        final = ans

    return {"final": final}


def memory_write_node(state: AgentState) -> AgentState:
    if state.get("memory_hit"):
        return {}

    final = (state.get("final") or "").strip()
    if not final:
        return {}

    q = state["query"]
    research = state.get("research", [])
    sources = [r["url"] for r in research if "url" in r]

    memory.save(q, final, sources)
    return {}



def planner_node(state: AgentState) -> AgentState:
    q = state["query"].strip()
    prompt = f"{SYSTEM}\n\n用一句計劃講你會點研究：\n問題：{q}"
    plan = llm.invoke(prompt).content
    log_event("planner", {"query": q, "plan": plan})
    return {"plan": plan}


def need_retry(state: AgentState) -> str:
    # 如果已經搜過2次，就唔再 retry
    if state.get("attempts", 0) >= 2:
        return "no_retry"

    # 如果 research 入面仲係好多非高質來源（因為 chosen 可能係 results）
    results = state.get("research", [])
    good, _ = split_by_quality(results)

    # 少過2個高質來源就 retry
    return "retry" if len(good) < 2 else "no_retry"


def research_node(state: AgentState) -> AgentState:
    base_q = state.get("next_query") or state["query"]
    q = base_q.strip()

    results = tavily_search(q, max_results=8)
    good, bad = split_by_quality(results)

    # 優先用 good，如果太少就暫時保留全部（下一個 conditional 會決定要唔要重搜）
    chosen = good if len(good) >= 2 else results

    log_event("research", {
        "query": q,
        "attempts": state.get("attempts", 0) + 1,
        "good_count": len(good),
        "bad_count": len(bad),
        "chosen_count": len(chosen),
        "results": results,
    })

    return {
        "research": chosen,
        "attempts": state.get("attempts", 0) + 1,
    }


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
- 主論點 bullets（最多 7 點）每點 必須 至少包含一個「資料列表」入面嘅 URL
- 如果某個論點搵唔到來源，唔好寫入主 bullets，改放到最後「Limitations」段落
- 只允許使用資料列表內出現過嘅 URL
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
- 主論點 bullets（最多 7 點）每點 必須 至少包含一個「資料列表」入面嘅 URL
- 如果某個論點搵唔到來源，唔好寫入主 bullets，改放到最後「Limitations」段落
- 只允許使用資料列表內出現過嘅 URL

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


def rewrite_query_node(state: AgentState) -> AgentState:
    q = state["query"].strip()
    prompt = f"""{SYSTEM}

你要改寫 search query，目標係搵到「官方/標準/技術來源」：
- 加上關鍵字：EIP, spec, proposal, standard, github, ethereum
- 盡量避免新聞炒作關鍵字
只輸出一行 query。

原問題：{q}
"""
    nq = llm.invoke(prompt).content.strip().strip('"')
    log_event("rewrite_query", {"query": q, "next_query": nq})
    return {"next_query": nq}


def evidence_gate_node(state: AgentState) -> AgentState:
    # check SUMMARY or FINAL (我建議 check summary 先，早啲重搜)
    summary = state.get("summary", "")
    ok = has_enough_evidence(summary, state.get(
        "research", []), min_cited_points=3)
    log_event("evidence_gate", {"ok": ok})
    return {"error": None if ok else "insufficient_evidence"}


def build_graph():
    g = StateGraph(AgentState)

    # --- nodes ---
    g.add_node("memory_search", memory_search_node)
    g.add_node("memory_answer", memory_answer_node)   # <= NEW
    g.add_node("planner", planner_node)
    g.add_node("rewrite_query", rewrite_query_node)
    g.add_node("research", research_node)
    g.add_node("summarize", summarize_node)
    g.add_node("evidence_gate", evidence_gate_node)
    g.add_node("critique", critique_node)
    g.add_node("refine", refine_node)
    g.add_node("memory_write", memory_write_node)

    # --- entry ---
    g.set_entry_point("memory_search")                # <= NEW

    # --- memory branching ---
    g.add_conditional_edges(
        "memory_search",
        lambda s: "use_memory" if s.get("memory_hit") else "do_research",
        {"use_memory": "memory_answer", "do_research": "planner"},
    )
    g.add_edge("memory_answer", END)                  # <= NEW

    # --- research flow ---
    g.add_edge("planner", "rewrite_query")
    g.add_edge("rewrite_query", "research")

    g.add_conditional_edges(
        "research",
        need_retry,
        {"retry": "rewrite_query", "no_retry": "summarize"},
    )

    g.add_edge("summarize", "evidence_gate")
    g.add_conditional_edges(
        "evidence_gate",
        lambda s: "retry" if s.get("error") else "ok",
        {"retry": "rewrite_query", "ok": "critique"},
    )

    g.add_edge("critique", "refine")
    g.add_edge("refine", "memory_write")
    g.add_edge("memory_write", END)

    return g.compile()
