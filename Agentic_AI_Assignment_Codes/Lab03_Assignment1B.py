"""Lab 3B: Low-evidence article must not cause invented evidence or limitations."""
ARTICLE = {"title":"New study announcement",
           "text":"A new campus application is the best application available."}
def apply_research_summary_skill(article):
    sentences = [s.strip() for s in article["text"].split(".") if s.strip()]
    claim = sentences[0] if sentences else "not stated in source"
    evidence_terms = ("because","measured","data","survey","sample","evaluation","compared","increased","reduced")
    evidence_sentences = [s for s in sentences[1:] if any(t in s.lower() for t in evidence_terms)]
    limitation_terms = ("limitation","however","small","only","may not","does not","unclear")
    limitations = [s for s in sentences if any(t in s.lower() for t in limitation_terms)]
    return {"claim":claim,
            "evidence":" ".join(evidence_sentences) if evidence_sentences else "not stated in source",
            "limitation":" ".join(limitations) if limitations else "not stated in source",
            "takeaway":"Do not generalize this claim without supporting evidence."}
if __name__ == "__main__":
    result = apply_research_summary_skill(ARTICLE)
    print(result)
    assert result["evidence"] == "not stated in source"
    assert result["limitation"] == "not stated in source"
    print("No fabrication occurred.")
