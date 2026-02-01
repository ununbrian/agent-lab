# Agent Lab — Project 0 (Playground)

> Goal: Build a runnable, debuggable LangGraph agent skeleton (research → summarize → critique → refine), with clean structure and trace logs for every node.

## What you have now

✅ A working LangGraph pipeline that runs end-to-end:
1. Planner
2. Research (stub)
3. Summarize
4. Critique
5. Refine (final output)

✅ Every step writes a JSONL trace into `app/logs/` so you can debug the graph like a backend workflow (not a black-box prompt).

✅ Clean project structure designed for future upgrades:
- Real web search + citations
- Memory layer (Qdrant)
- Tool routing / multi-tool plans
- Multi-agent orchestration
- Retry + guardrails + scoring

---

## Tech Stack

- Python (venv)
- LangGraph + LangChain Core
- OpenAI (ChatOpenAI)
- Pydantic + dotenv
- Rich (optional later)

---

## Folder Structure

```txt
agent-lab/
 ├─ app/
 │   ├─ graphs/           # LangGraph workflows
 │   │   └─ research_loop.py
 │   ├─ llm/              # LLM adapters
 │   │   └─ openai_client.py
 │   ├─ tools/            # Tools (search, shell, browser...)
 │   │   └─ search_stub.py
 │   ├─ types/            # Typed state definitions
 │   │   └─ state.py
 │   ├─ logs/             # JSONL traces per node execution
 │   │   └─ logger.py
 │   ├─ memory/           # reserved for Project 2 (Qdrant etc.)
 │   ├─ config.py
 │   └─ main.py
 ├─ scripts/
 ├─ .env                  # local secrets (DO NOT COMMIT)
 └─ .venv/                # local venv (DO NOT COMMIT)
