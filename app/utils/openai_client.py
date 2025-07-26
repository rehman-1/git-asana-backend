import openai
from app.asana.config import OPENAI_API_KEY

openai.api_key = OPENAI_API_KEY

def analyze_commit(code_diff: str, task_name: str):
    prompt = f"""
Task: {task_name}
Here is the developer's code diff or commit changes:

{code_diff}

Please:
1. Summarize what was done in simple terms.
2. Estimate the task completion progress in percentage.
3. Be honest if it looks partial or complete.

Format response as:
Summary: ...
Progress: ...%
"""

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.5,
    )
    return response['choices'][0]['message']['content']
