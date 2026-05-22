from tools import run_integration_test

class QA:
    def __init__(self, llm):
        self.llm = llm

    def write_tests(self, state):
        print("---QA: Writing Tests---")
        res = self.llm.invoke([("system", """You are a Python test generator.

Return ONLY valid executable Python code.
Do NOT include:
- explanations
- markdown
- comments outside code
- backticks
- prose
- headings

Output must be runnable as a .py file."""),
                                ("human", state['code'])])
        tests = res.content.replace("```python", "").replace("```", "").strip()
        return {"tests": tests}

    def run_tests(self, state):
        print("---QA: Executing Tests---")
        result = run_integration_test(state['code'], state['tests'])
        return {
            "terminal_output": result["output"],
            "is_fixed": result["success"],
            "retry_count": state.get("retry_count", 0) + 1
        }