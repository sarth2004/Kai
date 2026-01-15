import os
import wikipedia

from cache import get_from_cache, save_to_cache


KB_PATH = os.path.join(os.path.dirname(__file__), "kb")


def load_kb() -> list[str]:
    kb_texts = []

    for file in os.listdir(KB_PATH):
        if file.endswith(".txt"):
            file_path = os.path.join(KB_PATH, file)
            with open(file_path, "r", encoding="utf-8") as f:
                kb_texts.append(f.read())

    return kb_texts


def search_wikipedia(query: str) -> dict:
    # Check cache first
    cached = get_from_cache(query)
    if cached:
        return cached

    try:
        wikipedia.set_lang("en")
        page = wikipedia.page(query, auto_suggest=False)

        result = {
            "text": page.content,
            "source": page.url
        }

        save_to_cache(query, result)
        return result

    except Exception:
        return {
            "text": "No relevant information found.",
            "source": ""
        }

# import os
# import wikipedia
# from cache import get_from_cache, save_to_cache

# KB_PATH = "backend/kb/"

# def load_kb():
#     texts = []
#     for file in os.listdir(KB_PATH):
#         if file.endswith(".txt"):
#             with open(os.path.join(KB_PATH, file), "r", encoding="utf-8") as f:
#                 texts.append(f.read())
#     return texts

# def search_wikipedia(query):
#     cached = get_from_cache(query)
#     if cached:
#         return cached

#     try:
#         page = wikipedia.page(query, auto_suggest=False)
#         result = {"text": page.content, "source": page.url}
#         save_to_cache(query, result)
#         return result
#     except:
#         return {"text": "", "source": ""}
