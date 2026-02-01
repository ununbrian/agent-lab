import re
from typing import List, Dict
from urllib.parse import urlparse

URL_RE = re.compile(r"https?://[^\s)]+")
MD_URL_RE = re.compile(r"\((https?://[^\s)]+)\)")

def extract_urls(text: str) -> List[str]:
    # match markdown links and plain urls
    urls = MD_URL_RE.findall(text) + URL_RE.findall(text)
    # de-dup preserve order
    seen = set()
    out = []
    for u in urls:
        if u not in seen:
            seen.add(u)
            out.append(u)
    return out

def allowed_url_set(research: List[Dict[str, str]]) -> set:
    return set([r.get("url", "") for r in research if r.get("url")])

def has_enough_evidence(summary_or_final: str, research: List[Dict[str, str]], min_cited_points: int = 3) -> bool:
    allowed = allowed_url_set(research)
    used = [u for u in extract_urls(summary_or_final) if u in allowed]
    return len(set(used)) >= min_cited_points
