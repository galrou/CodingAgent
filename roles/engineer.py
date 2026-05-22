import os
from langchain_core.prompts import ChatPromptTemplate
from models import AgentState
from typing import Dict, Any
from workspace_sandbox import WorkspaceSandbox


class Engineer:
    def __init__(self, llm, sandbox: WorkspaceSandbox):
        self.llm = llm
        self.sandbox = sandbox  # Give the engineer awareness of the sandbox path location
        self._prompt = ChatPromptTemplate.from_messages([
            ("system", (
                "You are an expert software engineer executing a local task.\n"
                "Your objective is to write functional, correct Python code that satisfies the requirements.\n"
                "Return ONLY the clean executable Python code within markdown blocks. No extra fluff."
            )),
            ("user", "{prompt_body}")
        ])

    def write_code(self, state: AgentState) -> Dict[str, Any]:
        prompt_body = f"Task Requirement: {state['task_description']}\n\n"

        if state.get("retry_count", 0) > 0:
            prompt_body += (
                f"### ATTENTION: PREVIOUS ATTEMPT FAILED ###\n"
                f"Your last code implementation failed validation.\n\n"
                f"--- LAST TEST EXECUTION TERMINAL OUTPUT ---\n"
                f"{state['error_summary']}\n"
                f"-------------------------------------------\n\n"
                f"Please review your prior attempt. Identify the architectural flaw or bug, "
                f"and rewrite the solution to fix it entirely.\n"
            )
            if state.get("code_history"):
                prompt_body += f"--- YOUR PREVIOUS ATTEMPT ---\n{state['code_history'][-1]}\n\n"
        else:
            prompt_body += "This is your first attempt at the task. Write clean, complete implementation code."

        chain = self._prompt | self.llm
        response = chain.invoke({"prompt_body": prompt_body})

        generated_code = response.content.replace("```python", "").replace("```", "").strip()

        # --- FIX: Physically save the code to the sandbox disk location! ---
        file_target = state.get("current_file_path", "solution.py")
        absolute_target_path = os.path.join(self.sandbox.path, file_target)

        # Ensure directory sub-structures exist if the path is multi-level
        os.makedirs(os.path.dirname(absolute_target_path), exist_ok=True)

        with open(absolute_target_path, "w", encoding="utf-8") as f:
            f.write(generated_code)

        print(f"[Engineer] Successfully wrote code iteration to: {absolute_target_path}")
        # -----------------------------------------------------------------

        updated_history = state.get("code_history", []).copy()
        updated_history.append(generated_code)

        return {
            "code_history": updated_history,
            "current_file_path": file_target
        }