"""Lab 11B: independent acceptance tests catch an intentionally inverted filter bug."""
STORY={"acceptance_criteria":["only rows matching selected category are exported"]}
def testing_agent(story):
    # Tests derive only from requirements, not implementation.
    def test_filter(export_function):
        rows=[{"name":"A","category":"technical"},{"name":"B","category":"social"}]
        result=export_function(rows,"technical")
        return all(r["category"]=="technical" for r in result) and len(result)==1
    return [test_filter]
def coding_agent_buggy(rows,category):
    # DELIBERATE BUG: inverted comparison.
    return [r for r in rows if r["category"] != category]
if __name__ == "__main__":
    tests=testing_agent(STORY)
    for test in tests:
        passed=test(coding_agent_buggy)
        print("Independent acceptance test:", "PASS" if passed else "FAIL")
        assert not passed, "The deliberate bug should be detected."
    print("Regression detected: testing criteria were authored independently.")
