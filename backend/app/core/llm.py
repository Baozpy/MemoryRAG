from openai import OpenAI
import os

#chatgpt model
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)


def generate_answer(query: str, context: str):

    prompt = f"""
Context:
{context}

Question:
{query}

Answer based only on the context.
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response.choices[0].message.content



# # demo chact

# def generate_answer(query: str, context: str):
#     return f"""
# Question:
# {query}

# Retrieved Context:
# {context}

# This is a fake LLM response for testing MemoryRAG.
# """