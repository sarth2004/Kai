from sentence_transformers import SentenceTransformer
import faiss
import numpy as np


# Load embedding model once (important for performance)
embed_model = SentenceTransformer("all-MiniLM-L6-v2")


def chunk_text(text: str, size: int = 400) -> list[str]:
    paragraphs = text.split("\n\n")
    chunks = []

    for p in paragraphs:
        if len(p) > 50:
            chunks.append(p[:size])

    return chunks


def build_vector_store(chunks: list[str]):
    vectors = embed_model.encode(chunks)

    dimension = vectors.shape[1]
    index = faiss.IndexFlatL2(dimension)

    index.add(np.array(vectors))

    return index, vectors

# from sentence_transformers import SentenceTransformer
# import faiss
# import numpy as np

# embed_model = SentenceTransformer("all-MiniLM-L6-v2")

# def chunk_text(text, size=400):
#     paragraphs = text.split("\n\n")
#     return [p[:size] for p in paragraphs if len(p) > 50]

# def build_vector_store(chunks):
#     vectors = embed_model.encode(chunks)
#     index = faiss.IndexFlatL2(vectors.shape[1])
#     index.add(np.array(vectors))
#     return index
