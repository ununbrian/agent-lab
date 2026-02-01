# Agent Lab — Devlog

This repository is a project-based journey to build **production-grade AI agents**
using LangGraph and modern agent engineering techniques.

Focus:
- Verifiable research agents
- Tool routing & retry logic
- Evidence-based outputs
- Future memory & personal agent systems

---

## Project 0 — Agent Playground (Completed)

Goal:
Build a runnable LangGraph skeleton with full traceability.

Implemented:
- LangGraph workflow:
  planner → research → summarize → critique → refine
- Typed state (AgentState)
- Modular folder structure (graphs, tools, llm, memory)
- JSONL logs for every node execution

Key result:
A debuggable agent pipeline instead of a black-box prompt.

---

## Project 1 — Research Agent with Evidence Gate (Completed)

Goal:
Turn the playground into a **real research agent** with:
- Real web search
- Reliable sources
- Automatic retry
- No unsupported claims

Implemented:
- Tavily web search tool
- Source quality filter (high vs low quality domains)
- Query rewrite + auto retry
- Evidence gate:
  - Main bullets must have citations
  - Unsupported claims go to Limitations
- Structured output:
  - Main claims
  - Limitations
  - References

Workflow:

planner  
  ↓  
rewrite_query  
  ↓  
research (web search + source filter)  
  ↓  
(evidence gate & retry if needed)  
  ↓  
summarize  
  ↓  
critique  
  ↓  
refine  
  ↓  
FINAL OUTPUT  

Key result:
The agent produces **verifiable, source-backed analysis**
instead of speculative text.

---

## Current Capabilities

- Real-time web research
- Source quality control
- Automatic re-search if data is weak
- Evidence-based summarization
- Explicit uncertainty handling (Limitations)
- Full execution traces

---

## Tech Stack

- Python 3.11+
- LangGraph
- LangChain Core
- OpenAI / Claude (pluggable)
- Tavily Search API
- Pydantic
- dotenv

---

## Repository Structure

agent-lab/
  app/
    graphs/        LangGraph workflows
    llm/           LLM adapters
    tools/         Search, filters, gates
    types/         State definitions
    logs/          JSONL execution traces
    memory/        Reserved for Project 2
    main.py
    config.py
  .env             Secrets (not committed)
  .venv/           Local virtualenv (not committed)
  README.md

---

## How to Run

1. Activate venv:

source .venv/bin/activate

2. Set environment variables in .env:

OPENAI_API_KEY=your_key  
OPENAI_MODEL=gpt-4.1-mini  
TAVILY_API_KEY=your_key  

3. Run:

python -m app.main "ERC-8004 對 ETH 幣價可能有咩影響？"

---

## Philosophy

Engineering > Prompting  
Verification > Fluency  
Workflow > Single Call  

Goal:
Build agents that:
- can retry safely
- justify outputs with sources
- evolve into personal or enterprise systems

---

## Next Project

Project 2 — Memory Agent (Qdrant)

Planned:
- Episodic memory (store past research results)
- Semantic retrieval
- Query reuse / cache
- User profile memory

Target behavior:

"What did I find about ERC-8004 last time?"

Agent should:
- retrieve previous result
- update with new data
- merge into final answer
