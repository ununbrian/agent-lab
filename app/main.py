import sys
from app.graphs.research_loop import build_graph

def main():
    if len(sys.argv) < 2:
        print('Usage: python -m app.main "你的問題"')
        raise SystemExit(1)

    query = sys.argv[1]
    graph = build_graph()

    state = {"query": query}
    out = graph.invoke(state)

    print("\n=== FINAL ===\n")
    print(out.get("final", "(no output)"))

if __name__ == "__main__":
    main()
