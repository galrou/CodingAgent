import subprocess

def run_integration_test(code: str, tests: str):
    """Executes code and tests, returns the terminal output."""
    with open("temp_code.py", "w") as f: f.write(code)
    with open("temp_test.py", "w") as f: f.write(tests)

    # Run the test
    result = subprocess.run(
        ["python", "temp_test.py"],
        capture_output=True,
        text=True
    )

    # Cleanup (Optional)
    # os.remove("temp_code.py")
    # os.remove("temp_test.py")

    return {
        "success": result.returncode == 0,
        "output": f"STDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
    }


def save_final_files(code: str, readme: str):
    with open("generated_code.py", "w") as f: f.write(code)
    with open("README.md", "w") as f: f.write(readme)