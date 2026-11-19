"""Lab 11A: process two stories and retain artifact lineage per story."""
STORIES=[
 {"id":"US-1","feature":"CSV export","criteria":["file ends in .csv","applied filters are preserved"]},
 {"id":"US-2","feature":"PDF export","criteria":["file ends in .pdf","applied filters are preserved"]}
]
def design_agent(story):
    return {"story_id":story["id"],"design":f"Add {story['feature']} action and export service."}
def coding_agent(story,design):
    return {"story_id":story["id"],"design_story_id":design["story_id"],
            "code_artifact":f"{story['feature'].replace(' ','_').lower()}_export.py"}
def testing_agent(story):
    return {"story_id":story["id"],"tests":[f"test {c}" for c in story["criteria"]]}
if __name__ == "__main__":
    lineage=[]
    for story in STORIES:
        design=design_agent(story); code=coding_agent(story,design); tests=testing_agent(story)
        lineage.append({"story_id":story["id"],"design":design,"code":code,"tests":tests})
    print("Lineage:",lineage)
    assert all(x["story_id"]==x["code"]["story_id"]==x["tests"]["story_id"] for x in lineage)
