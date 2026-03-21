import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key=os.environ["GEMINI_API_KEY"])

EMBEDDING_MODEL = "models/gemini-embedding-001"

def embed_text(text: str) -> list[float]:
    try:
        result = genai.embed_content(
            model=EMBEDDING_MODEL,
            content=text,
            task_type="retrieval_document"
        )
        return result["embedding"]
    except Exception as e:
        print(f"Embedding failed: {e}")
        return []

def embed_query(text: str) -> list[float]:
    try:
        result = genai.embed_content(
            model=EMBEDDING_MODEL,
            content=text,
            task_type="retrieval_query"
        )
        return result["embedding"]
    except Exception as e:
        print(f"Query embedding failed: {e}")
        return []

def embed_article(article: dict) -> list[float]:
    text = f"{article.get('title', '')} {article.get('snippet', '')}"
    text = text.strip()
    if not text:
        return []
    return embed_text(text)