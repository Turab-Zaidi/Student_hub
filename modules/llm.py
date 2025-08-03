from langchain_google_genai import GoogleGenerativeAI

def call_llm(prompt,tokens=512):
    llm = GoogleGenerativeAI(model="gemini-2.5-flash-lite",
            temp = 0.2,
            max_tokens = tokens
    )
    return llm.invoke(prompt).strip()