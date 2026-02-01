from typing import TypedDict, List, Dict, Optional

class AgentState(TypedDict, total=False):
    query: str
    plan: str
    research: List[Dict[str, str]]
    summary: str
    critique: str
    final: str
    error: Optional[str]
    attempts: int
    next_query: str
