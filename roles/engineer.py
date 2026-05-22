class Engineer:
    def __init__(self, llm):
        self.llm = llm

    def code_editor(self, state):
        print("---ENGINEER: Writing Code---")
        prompt = f"Task: {state['task']}\nErrors: {state.get('terminal_output', 'None')}\nCode: {state.get('code', '')}"

        res = self.llm.invoke([("system", "Write ONLY python code."), ("human", prompt)])
        code = res.content.replace("```python", "").replace("```", "").strip()
        return {"code": code, "is_fixed": False}

