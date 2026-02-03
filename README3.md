
# Agent Lab — Project 2 (Memory Agent)

> Goal: Upgrade the research agent with **episodic memory** so it can reuse past results and avoid repeated web research for similar questions.

---

## What this project adds

🧠 **Persistent memory (Qdrant)**
- Store each completed research result as a memory record:
  - query
  - final answer
  - sources (URLs)
- Uses vector embeddings for semantic search.

⚡ **Bypass research on memory hit**
- On new query:
  - First search memory
  - If similar result exists → return memory answer directly
  - Skip planner / research / summarize / critique
- Saves:
  - API calls
  - tokens
  - latency

🔁 **Write memory only on fresh research**
- If answer comes from memory:
  - Do NOT write again (avoid duplicates)
- Only store when:
  - A new full research cycle completes
  - `final` output is non-empty

---

## Workflow

```

memory_search
↓
(memory hit?) ── yes ──→ memory_answer → END
│
no
↓
planner
↓
rewrite_query
↓
research
↓
summarize
↓
evidence_gate (retry if weak)
↓
critique
↓
refine
↓
memory_write
↓
END

````

---

## Tech Stack (added in Project 2)

- Qdrant (vector database, via Docker)
- sentence-transformers (all-MiniLM-L6-v2)
- qdrant-client
- LangGraph conditional routing

---

## Memory Design

Each memory entry contains:

```json
{
  "query": "ERC-8004 對 ETH 幣價可能有咩影響？",
  "answer": "...final refined answer...",
  "sources": [
    "https://eips.ethereum.org/EIPS/eip-8004",
    "https://github.com/erc-8004/erc-8004-contracts"
  ]
}
````

Stored as:

* vector = embedding(answer)
* payload = { query, answer, sources }

---

## Behavior

### First time:

```bash
python -m app.main "ERC-8004 對ETH幣價可能有咩影響？"
```

→ full research
→ result saved to memory

### Second time (similar question):

```bash
python -m app.main "ERC-8004 重點係咩？"
```

→ memory hit
→ return stored answer
→ no web search
→ no retry loop

---

## Guarantees

* Never returns memory hit with empty answer
* Never stores empty answers into memory
* Research is only triggered when memory is missing or insufficient
* Output still follows:

  * cited bullets
  * limitations section
  * explicit sources

---

## Current State

* Project 0: Agent workflow skeleton ✅
* Project 1: Evidence-based research agent ✅
* Project 2: Memory agent with bypass logic ✅

Current version ≈ `v0.2`

---

## Next Direction (Project 3 options)

Possible upgrades:

* Semantic cache + merge new updates
* User profile memory (preferences, portfolio)
* Multi-agent roles (researcher / critic / planner)
* Long-term memory decay / scoring
* Tool routing based on task type

---

## Philosophy

Prompting teaches the model.
Workflow teaches the system.
Memory teaches the agent.

This project shifts the agent from:

> stateless LLM calls
> to:
> stateful research assistant with recall
