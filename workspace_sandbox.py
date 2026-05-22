import os
import subprocess
import sys
import tempfile
from typing import Dict, Any


class WorkspaceSandbox:
    """
    Manages an isolated, disposable Git worktree environment to execute
    and test LLM-generated code safely without modifying active files.
    """

    def __init__(self, branch_name: str = "agent-sandbox-fix"):
        self.branch_name = branch_name
        self.path = os.path.join(tempfile.gettempdir(), f"coding_agent_{self.branch_name}")
        self.is_active = False

    def create(self) -> str:
        if self.is_active:
            return self.path

        try:
            subprocess.run(
                ["git", "worktree", "add", "-b", self.branch_name, self.path, "main"],
                check=True,
                capture_output=True,
                text=True
            )
            self.is_active = True
            print(f"[Sandbox] Isolated workspace deployed at: {self.path}")
            return self.path
        except subprocess.CalledProcessError as e:
            # If directory or branch already exists, we recover gracefully
            print(f"[Sandbox] Warning: Initial creation encountered fallback: {e.stderr.strip()}")
            self.is_active = True
            return self.path


    def run_tests(self, test_command: str = "pytest", timeout_seconds: int = 15) -> Dict[str, Any]:
        """Runs test execution strictly contained within the sandbox with a kill switch."""
        if not self.is_active or not os.path.exists(self.path):
            return {"success": False, "output": "ERROR: Sandbox environment is not initialized."}

        try:
            # 1. Grab your active virtual environment paths from PyCharm
            current_env = os.environ.copy()

            # 2. Automatically wrap the command through your active python interpreter
            # If test_command is "pytest", this becomes: "C:\...\.venv\Scripts\python.exe" -m pytest
            if test_command == "pytest":
                cmd = f'"{sys.executable}" -m pytest'
            else:
                cmd = test_command

            print(f"[Sandbox] Running command: {cmd}")

            result = subprocess.run(
                cmd,
                cwd=self.path,
                capture_output=True,
                text=True,
                timeout=timeout_seconds,
                shell=True,
                env=current_env
            )
            return {
                "success": result.returncode == 0,
                "output": result.stdout if result.returncode == 0 else result.stderr
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "output": f"ERROR: Execution exceeded timeout boundary of {timeout_seconds}s. Code loop killed."
            }

    def cleanup(self) -> None:
        """Safely tears down and deletes the worktree metadata and temporary directory."""
        if not self.is_active:
            return

        print(f"[Sandbox] Tearing down workspace: {self.path}")
        # Wipe git connection
        subprocess.run(["git", "worktree", "remove", "--force", self.path], capture_output=True)
        # Drop temporary local git branch tracking it
        subprocess.run(["git", "branch", "-D", self.branch_name], capture_output=True)
        self.is_active = False