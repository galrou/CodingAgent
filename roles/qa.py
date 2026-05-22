import os

class QA:
    def __init__(self, llm):
        self.llm = llm

    def write_tests(self, state):
        print("---QA: Writing Tests---")
        res = self.llm.invoke([("system", """You are a Python test generator.
Make sure you import the function from 'solution'. E.g., 'from solution import ...'

Return ONLY valid executable Python code.
Do NOT include explanations, markdown, or backticks."""),
                               ("human", f"Code to test:\n{state['code']}")])

        tests = res.content.replace("```python", "").replace("```", "").strip()

        # ---> OOP BEST PRACTICE: Write the test file to the sandbox <---
        sandbox_dir = state["sandbox_path"]
        test_path = os.path.join(sandbox_dir, "test_solution.py")
        os.makedirs(os.path.dirname(test_path), exist_ok=True)
        with open(test_path, "w", encoding="utf-8") as f:
            f.write(tests)

        print(f"[QA] Saved test suite to sandbox: {test_path}")
        return {"tests": tests}