import warnings
import os
from dotenv import load_dotenv

from langchain_groq import ChatGroq

from graph import create_app

warnings.filterwarnings("ignore")
load_dotenv()

def main():
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY environment variable not set. Please add it to your .env file.")

    llm = ChatGroq(
        api_key=api_key,
        model="llama-3.3-70b-versatile",
        temperature=0
    )
    app = create_app(llm)

    task = "Write a python function that checks if a string is a palindrome and add logging (and check that the logging works)."
    initial_input = {
        "task": task,
        "code": "",
        "test_results": "None",
        "is_fixed": False,
        "retry_count": 0
    }
    for event in app.stream(initial_input):
        print(event)

if __name__ == "__main__":
    main()

