# Kai - Educational AI Assistant

A local RAG (Retrieval-Augmented Generation) based AI assistant that uses Ollama (Phi model) to answer questions with context from Wikipedia and a local knowledge base.

## Features
- **RAG Pipeline**: Combines local text files and Wikipedia searches to answer questions.
- **Local LLM**: Uses Ollama (Phi model) for privacy and offline capability.
- **Streaming Responses**: Real-time "typing" effect for answers.
- **Markdown & Syntax Highlighting**: Beautifully formatted code blocks and text.

## Prerequisites

1.  **Python 3.10+** installed.
2.  **Ollama** installed and running.
    -   Download from [ollama.com](https://ollama.com).
    -   Pull the model: `ollama pull phi`

## Installation

1.  Clone or download this repository.
2.  Open a terminal in the project folder (`Kai`).
3.  Install the required Python packages:

    ```bash
    pip install -r requirements.txt
    ```

## Running the Application

### 1. Start the Backend

Open a terminal, navigate to the `backend` directory, and run the FastAPI server:

```bash
cd backend
uvicorn main:app --reload
```

You should see output indicating the server is running at `http://127.0.0.1:8000`.

### 2. Open the Frontend

Simply open the `index.html` file located in the `frontend` folder in your web browser.

You can do this by:
- Double-clicking `frontend/index.html` in your file explorer.
- Or extending your VS Code Live Server to view it.

## Usage

1.  Type a question in the text box (e.g., "Explain recursion in Python").
2.  Click **Ask**.
3.  The AI will "think" and then start streaming the answer.

## Troubleshooting

-   **Backend not reachable**: Make sure the terminal running `uvicorn` is still open and has no errors.
-   **Ollama connection error**: Ensure Ollama is running (`ollama list` in a new terminal should show `phi`).
