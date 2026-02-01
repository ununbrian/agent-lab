from typing import List, Dict

def web_search_stub(query: str) -> List[Dict[str, str]]:
    # TODO: Project 1 會接真正 search provider（Tavily / Serp / custom）
    # 依家先用假資料，確保 graph 架構同 debug flow 都先跑通。
    return [
        {"title": "Stub result 1", "url": "https://example.com/1", "snippet": f"Result for: {query}"},
        {"title": "Stub result 2", "url": "https://example.com/2", "snippet": "More context here..."},
    ]
