"""Lab 3A: Select the best-supported claim from a multi-claim article."""
ARTICLE = {
 "title":"AI platform report",
 "text":("The platform reduced operating cost by 20%. The evaluation included 500 tasks "
         "across three test runs. The platform also improved accuracy by 8%. "
         "Accuracy was measured on 1,000 labelled examples using a held-out test set.")
}
def apply_research_summary_skill(article):
    text = article["text"]
    sentences = [s.strip() for s in text.split(".") if s.strip()]
    claims = [s for s in sentences if "%" in s]
    # Evidence-bearing claims are paired with the next sentence containing evaluation details.
    candidates = []
    for claim in claims:
        idx = sentences.index(claim)
        evidence = sentences[idx+1] if idx+1 < len(sentences) else "not stated in source"
        score = sum(k in evidence.lower() for k in ("evaluation","tasks","test","examples","measured"))
        candidates.append((score, claim, evidence))
    candidates.sort(reverse=True)
    score, claim, evidence = candidates[0]
    return {"claim":claim, "evidence":evidence,
            "selection_note":f"Selected from {len(claims)} competing claims because it has the strongest explicit evidence.",
            "limitation":"not stated in source" if len(sentences) <= 2 else sentences[-1],
            "takeaway":claim + " — interpret within the reported evaluation."}
if __name__ == "__main__":
    print(apply_research_summary_skill(ARTICLE))
