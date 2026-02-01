from urllib.parse import urlparse
from typing import List, Dict, Tuple

# 你可以慢慢擴充呢個 allowlist
HIGH_QUALITY_DOMAINS = {
    "eips.ethereum.org",
    "ethereum.org",
    "github.com",
    "docs.openzeppelin.com",
    "consensys.io",
    "coindesk.com",
    "theblock.co",
    "cointelegraph.com",
    "arxiv.org",
}

LOW_QUALITY_DOMAINS = {
    "threads.com",
    "tiktok.com",
    "instagram.com",
    "facebook.com",
    "podcasts.apple.com",
}

def split_by_quality(results: List[Dict[str, str]]) -> Tuple[List[Dict[str, str]], List[Dict[str, str]]]:
    good, bad = [], []
    for r in results:
        host = urlparse(r.get("url", "")).netloc.lower().replace("www.", "")
        if host in LOW_QUALITY_DOMAINS:
            bad.append(r)
        elif host in HIGH_QUALITY_DOMAINS:
            good.append(r)
        else:
            # 未知域名：先當中立，但唔算 high-quality
            bad.append(r)
    return good, bad
