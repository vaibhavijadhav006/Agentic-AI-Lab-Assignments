"""Lab 9B: source quality tiers guide synthesis without hiding weaker evidence."""
SOURCES=[
 {"id":"S1","claim":"RAG reduces hallucinations by 41%.","tier":"peer_reviewed","quality":3},
 {"id":"S4","claim":"RAG shows no measurable improvement.","tier":"vendor_blog","quality":1}
]
def synthesize(sources):
    ranked=sorted(sources,key=lambda s:s["quality"],reverse=True)
    return {"leans_toward":ranked[0]["id"],"reason":f"{ranked[0]['tier']} source receives greater evidential weight.",
            "weighted_claim":ranked[0]["claim"],
            "disclosure":f"Down-weighted, not discarded: {ranked[1]['id']} ({ranked[1]['tier']}) says: {ranked[1]['claim']}",
            "caveat":"A quality tier is a prioritization aid, not proof that a claim is true."}
if __name__ == "__main__": print(synthesize(SOURCES))
