因為你係「直接由 GitHub / UI copy 落嚟」，啲 **`bash / Copy code / txt` 標籤係 GitHub UI 注入嘅**，唔係 Markdown 本身，所以變咗垃圾字。

我而家幫你 **還原成 100% 正確、乾淨、可 copy-paste 嘅 README.md**。
👉 你只需要：**由 `md 到 ` 全選 copy，覆蓋你 README.md 內容。**

---

````md
# Agent Lab — Project 0 (Playground)

> Goal: Build a runnable, debuggable LangGraph agent skeleton  
> (research → summarize → critique → refine), with clean structure and trace logs for every node.

---

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
````

---

## How to Run

### 1) Activate venv

```bash
source .venv/bin/activate
```

### 2) Create `.env`

```bash
OPENAI_API_KEY=YOUR_KEY
OPENAI_MODEL=gpt-4.1-mini
```

### 3) Run

```bash
python -m app.main "Pendle sPENDLE 對幣價可能有咩影響？"
```

---

## Debug Traces

After running, check:

```bash
ls app/logs
```

You should see files like:

```txt
YYYYMMDD-HHMMSS-planner.jsonl
YYYYMMDD-HHMMSS-research.jsonl
YYYYMMDD-HHMMSS-summary.jsonl
YYYYMMDD-HHMMSS-critique.jsonl
YYYYMMDD-HHMMSS-final.jsonl
```

Each file contains JSON lines with node inputs/outputs.

---

## Current Limitation (Intentional)

* `web_search_stub()` is a stub, so URLs are placeholders.

---

## Next Milestone (Project 1)

Replace stub with:

* Real web search
* Citations
* Auto retry logic

