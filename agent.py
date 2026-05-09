import subprocess
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from models import AgentState, prompts


class Agent:
    def __init__(self, model_name: str, api_key: str):
        self.llm = ChatGroq(model=model_name, temperature=0, api_key=api_key)

    def _call_llm(self, sys_msg, human_msg, input_data):
        prompt = ChatPromptTemplate.from_messages([
            ("system", sys_msg),
            ("human", human_msg)
        ])
        return (prompt | self.llm).invoke(input_data).content

    def code_editor(self, state: AgentState):
        print("---CODER: Writing/Fixing Code---")
        # We pass the terminal output if it exists so the coder can see the real error
        res = self._call_llm(prompts.CoderPrompts.System, prompts.CoderPrompts.Human, state)
        code = res.replace("```python", "").replace("```", "").strip()
        return {"code": code, "is_fixed": False}

    def test_writer(self, state: AgentState):
        print("---TEST WRITER: Creating Unit Tests---")
        # We ask for a script that tests the specific code generated
        sys_msg = "You are a QA Engineer. Write a Python script using 'unittest' or 'pytest'. Write ONLY code."
        human_msg = f"Task: {state['task']}\nCode: {state['code']}\nWrite tests to verify this works."
        res = self._call_llm(sys_msg, human_msg, {})
        return {"tests": res.replace("```python", "").replace("```", "").strip()}

    def executor(self, state: AgentState):
        """Node that actually runs the code and tests on your machine"""
        print("---EXECUTOR: Running Subprocess Tests---")

        # Save temp files for execution
        with open("temp_code.py", "w") as f: f.write(state["code"])
        with open("temp_test.py", "w") as f: f.write(state["tests"])

        # Run the test file
        result = subprocess.run(
            ["python", "temp_test.py"],
            capture_output=True,
            text=True
        )

        # Combine stdout and stderr for the full terminal picture
        full_output = f"STDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
        success = result.returncode == 0

        print(f"Tests {'PASSED' if success else 'FAILED'}")

        return {
            "terminal_output": full_output,
            "is_fixed": success,
            "test_results": "Pass" if success else "Fail"
        }

    def documenter(self, state: AgentState):
        """Node to generate the PR documentation"""
        print("---DOCUMENTER: Writing README.md---")
        sys_msg = "You are a Technical Writer. Summarize the coding task and the test results for a Pull Request."
        human_msg = f"Task: {state['task']}\nTests Run:\n{state['tests']}\nTerminal Results:\n{state['terminal_output']}"

        readme_content = self._call_llm(sys_msg, human_msg, {})

        with open("README.md", "w") as f:
            f.write(readme_content)
        return state

    @staticmethod
    def file_saver(state: AgentState):
        print("---SAVER: Saving to file---")
        with open("generated_code.py", "w") as f:
            f.write(state["code"])
        return state