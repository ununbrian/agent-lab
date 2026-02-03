from typing import TypedDict, List, Dict, Optional

class AgentState(TypedDict):
    query: str
    plan: str
    research: list
    summary: str
    critique: str
    final: str          
    memory_hit: bool
    memory_answer: str
    memory_sources: list
    attempts: int
    next_query: str
