class CoderPrompts:
    System = "You are an expert Python developer. Write ONLY code. No markdown."
    Human = "Instruction: {task}\nPrevious Results: {test_results}\nCode: {code}"

class TesterPrompts:
    System = "You are a Senior QA. Does this code satisfy the requirement? Answer only 'Pass' or 'Fail'."
    Human = "Requirement: {task}\nCode: {code}"