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

    def __init__(self, branch_name: str = "agent-sandbox"):
        self.branch_name = branch_name
        self.path = os.path.join(tempfile.gettempdir(), f"coding_agent_{self.branch_name}")
        self.is_active = False

    def create(self) -> str:
        if self.is_active:
            return self.path

        # Clean up directory path on disk if it exists from a dead process
        if os.path.exists(self.path):
            try:
                subprocess.run(["git", "worktree", "remove", "--force", self.path], capture_output=True)
                subprocess.run(["git", "branch", "-D", self.branch_name], capture_output=True)
            except Exception:
                pass

        try:
            subprocess.run(
                ["git", "worktree", "add", "-b", self.branch_name, self.path, "HEAD"],
                check=True,
                capture_output=True,
                text=True
            )
            self.is_active = True
            print(f"[Sandbox] Isolated workspace deployed at: {self.path}")
            return self.path
        except subprocess.CalledProcessError as e:
            print(f"[Sandbox] Critical Failure creating worktree: {e.stderr.strip()}")
            # Do not pretend things are okay if Git fails to deploy the structure
            raise e

    def run_tests(self, test_target: str = "solution.py", timeout_seconds: int = 15) -> Dict[str, Any]:
        """Runs test or script execution strictly contained within the sandbox with a kill switch."""
        if not self.is_active or not os.path.exists(self.path):
            return {"success": False, "output": "ERROR: Sandbox environment is not initialized."}

        try:
            current_env = os.environ.copy()

            # FIX 1: Use sys.executable directly without adding hardcoded string quotes
            python_executable = sys.executable

            absolute_file = os.path.join(self.path, test_target)
            has_tests = False

            if os.path.exists(absolute_file):
                with open(absolute_file, "r", encoding="utf-8") as f:
                    content = f.read()
                    if "def test_" in content:
                        has_tests = True

            # FIX 2: Define cmd strictly as a LIST of strings
            if has_tests:
                cmd = [python_executable, "-m", "pytest", test_target]
            else:
                cmd = [python_executable, "-u", test_target]

            # Log out a readable version of the command
            print(f"[Sandbox] Running tool command: {' '.join(cmd)}")

            # FIX 3: Pass the list, keep shell=False
            result = subprocess.run(
                cmd,
                cwd=self.path,
                capture_output=True,
                text=True,
                timeout=timeout_seconds,
                shell=False,
                env=current_env
            )

            # Merging both channels guarantees we pick up all text outputs, print statements, and crashes
            combined_output = (result.stdout or "") + "\n" + (result.stderr or "")

            return {
                "success": result.returncode == 0,
                "output": combined_output.strip()
            }

        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "output": f"ERROR: Execution exceeded timeout boundary of {timeout_seconds}s. Code loop killed."
            }
        except Exception as e:
            return {
                "success": False,
                "output": f"ERROR: Internal sandbox execution crash: {str(e)}"
            }

    def cleanup(self) -> None:
        """Safely tears down and deletes the worktree metadata and temporary directory."""
        if not self.is_active:
            return

        print(f"[Sandbox] Tearing down workspace: {self.path}")
        subprocess.run(["git", "worktree", "remove", "--force", self.path], capture_output=True)
        subprocess.run(["git", "branch", "-D", self.branch_name], capture_output=True)
        self.is_active = False