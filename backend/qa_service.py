from openai import OpenAI
from config import DEEPSEEK_API_KEY

client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url="https://api.deepseek.com/v1")

def get_answer_from_llm(question: str, context: str):
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": "You are a professional academic assistant. Please answer the user's question based on the provided context. If the context does not contain the answer, state that you cannot answer based on the given information."},
            {"role": "user", "content": f"Based on the following context, please answer the question.\n\nContext:\n\"\"\"\n{context}\n\"\"\"\n\nQuestion: {question}"},
        ],
        stream=False
    )
    return response.choices[0].message.content