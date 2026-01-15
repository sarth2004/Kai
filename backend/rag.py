import json
import httpx
import numpy as np

from embeddings import embed_model, build_vector_store, chunk_text


SYSTEM_PROMPT = """
You are an educational AI assistant.
You can generate **basic code examples** in Python, Java, or JavaScript.
**Format all code examples using Markdown code blocks** (e.g., ```python ... ```).
Explain the code step-by-step.
Use ONLY the provided context.
If context is insufficient, say "Insufficient information".
Cite the source if applicable.
"""


async def run_llm_stream(context: str, question: str, source: str = ""):
    prompt = f"""
{SYSTEM_PROMPT}

Context:
{context}

Question:
{question}

Source:
{source}

Answer:
"""

    print("DEBUG: Calling Ollama API (streaming)...")
    url = "http://localhost:11434/api/generate"
    payload = {
        "model": "phi",
        "prompt": prompt,
        "stream": True
    }

    try:
        async with httpx.AsyncClient(timeout=60) as client:
            async with client.stream("POST", url, json=payload) as response:
                async for chunk in response.aiter_lines():
                    if chunk:
                        try:
                            data = json.loads(chunk)
                            token = data.get("response", "")
                            if token:
                                yield token
                            if data.get("done", False):
                                break
                        except json.JSONDecodeError:
                            continue
        
        print("DEBUG: Ollama stream finished.")
        
    except Exception as e:
        print(f"ERROR: Ollama API error: {e}")
        yield f"\n[Error: {str(e)}]"


async def rag_pipeline(wiki_result: dict, kb_results: list[str], question: str):
    # Combine Wikipedia + KB text
    all_text = wiki_result["text"] + "\n\n" + "\n\n".join(kb_results)

    # Chunk documents
    chunks = chunk_text(all_text)

    # Build vector index
    index, vectors = build_vector_store(chunks)

    # Embed query
    query_vector = embed_model.encode([question])

    # Similarity search (top-3 chunks)
    _, indices = index.search(np.array(query_vector), k=3)

    # Retrieve top context
    top_context = "\n\n".join(chunks[i] for i in indices[0])

    # Run LLM with retrieved context (streaming)
    async for token in run_llm_stream(top_context, question, wiki_result.get("source", "")):
        yield token

    # Append source at the end
    source = wiki_result.get("source", "")
    if source:
        yield f"\n\nSource: {source}"

# import subprocess
# import numpy as np
# from embeddings import embed_model, build_vector_store, chunk_text

# SYSTEM_PROMPT = """
# You are an educational AI assistant.
# Generate basic code examples.
# Explain step by step.
# Use ONLY provided context.
# """

# def run_llm(context, question, source):
#     prompt = f"""
# {SYSTEM_PROMPT}

# Context:
# {context}

# Question:
# {question}

# Source: {source}

# Answer:
# """
#     result = subprocess.run(
#         ["ollama", "run", "mistral"],
#         input=prompt,
#         text=True,
#         capture_output=True
#     )
#     return result.stdout.strip()

# def rag_pipeline(wiki, kb, question):
#     text = wiki["text"] + "\n\n" + "\n\n".join(kb)
#     chunks = chunk_text(text)
#     index = build_vector_store(chunks)

#     q_vec = embed_model.encode([question])
#     _, idx = index.search(np.array(q_vec), 3)
#     context = "\n\n".join([chunks[i] for i in idx[0]])

#     return run_llm(context, question, wiki["source"])
