import os

# Fetch the API key from the environment variable
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Check if the API key was successfully loaded
if OPENAI_API_KEY is None:
    raise ValueError("OpenAI API key not found. Please set the environment variable.")
