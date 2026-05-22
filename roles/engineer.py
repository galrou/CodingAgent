import os

class Engineer:
    def __init__(self, llm):
        self.llm = llm

    def code_editor(self, state):
        print("---ENGINEER: Writing Code---")
        errors = state.get("terminal_output", "None")
        prompt = f"Task: {state['task']}\nErrors: {errors}\nCode: {state.get('code', '')}"

        res = self.llm.invoke([("system", "Write ONLY python code."), ("human", prompt)])
        code = res.content.replace("```python", "").replace("```", "").strip()

        # ---> OOP BEST PRACTICE: Write the code to a file inside the sandbox <---
        sandbox_dir = state["sandbox_path"]
        file_path = os.path.join(sandbox_dir, "solution.py")
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(code)

        print(f"[Engineer] Saved code to sandbox: {file_path}")
        return {"code": code, "is_fixed": False}