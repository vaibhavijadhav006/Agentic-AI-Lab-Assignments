"""Lab 9A: distinguish a direct contradiction from a missing evidence gap."""
SOURCES={
"S1":{"claim":"RAG reduces hallucinations by 41%.","domain":"medical QA","method":"200 held-out questions","quality":"peer-reviewed"},
"S2":{"claim":"RAG improves traceability.","domain":"enterprise QA","method":"case study","quality":"independent benchmark"},
"S3":{"claim":"RAG needs retrieval quality controls.","domain":"technical QA","method":"analysis","quality":"peer-reviewed"},
"S4":{"claim":"RAG showed no measurable hallucination improvement.","domain":"general QA","method":"different benchmark with 50 prompts","quality":"independent benchmark"}
}
def compare(a,b):
    direct=(("reduces hallucinations" in a["claim"] and "no measurable" in b["claim"]) or
            ("no measurable" in a["claim"] and "reduces hallucinations" in b["claim"]))
    return {"type":"genuine_conflict" if direct else "no_direct_conflict",
            "reason":"The evaluations use different domains, datasets, and sample sizes." if direct else "No direct contradiction identified."}
def synthesize(sources):
    conflict=compare(sources["S1"],sources["S4"])
    return {"summary":"Evidence on RAG's hallucination reduction is mixed.",
            "conflict":conflict,"disclosure":"S1 reports a 41% reduction; S4 reports no measurable improvement. Neither result should be generalized without considering methodology."}
if __name__ == "__main__":
    print(synthesize(SOURCES))
