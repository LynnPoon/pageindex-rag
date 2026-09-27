# PageIndex RAG

A small Python project for uploading PDFs to PageIndex and chatting with them
from the terminal. When the app starts, you can upload a new PDF or reuse a
previously saved document without uploading it again.

## Demo

Watch the project demo [here](https://youtu.be/KWMCSZdgw1Q).

## What It Does

- Prompts you to upload a new PDF or reuse a previously uploaded one.
- Saves the returned `doc_id` in `data/<pdf-name>.json`.
- Optionally saves the PageIndex document tree in `data/<pdf-name>_tree.json`.
- Starts an interactive chat session against a saved document.
- Streams answers in the terminal with citations enabled by the PageIndex API.

## Requirements

- Python 3.12
- `uv`
- A PageIndex API key
- One or more PDF files to ingest

## Setup

Install the project dependencies:

```powershell
uv sync
```

Create a `.env` file in the project root:

```env
PAGEINDEX_API_KEY=your_pageindex_api_key_here
```

The application loads this value automatically with `python-dotenv`.

## Upload or Reuse a PDF Interactively

Start the terminal assistant:

```powershell
uv run python -m src.cli
```

Put PDFs under `docs/` or provide any local PDF path. The repository ignores
`docs/*`, so local documents are not committed by default.

The first prompt gives you two choices:

- To upload a new PDF, enter its local path, such as `docs/report.pdf`. The app
  uploads and processes the file, then saves its document ID in `data/`.
- To reuse a saved document, press Enter without typing a path. This avoids a
  new upload.

Next, enter the saved PDF name without `.pdf`. For example, for
`docs/report.pdf`, enter:

```text
report
```

You can then ask questions about the document. Type `exit` or `quit` to stop.

Uploading sends the PDF to PageIndex and may use API credits. Reusing a saved
document only requires its corresponding `data/<pdf-name>.json` file.

## Upload a PDF Without Starting Chat

If you only want to ingest a document, use the ingestion helper:

```powershell
uv run python -c "from src.ingest import ingest; ingest('docs/report.pdf')"
```

It creates a local record such as `data/report.json`, which the interactive
assistant can reuse later.

## Programmatic Usage

You can also call the query engine directly:

```python
from src.ingest import load_doc_id
from src.query import DocumentChat

doc_id = load_doc_id("report")
chat = DocumentChat(doc_id)

answer = chat.ask("What are the main findings?")
print(answer)
```

For streaming answers:

```python
for token in chat.ask_stream("Summarize the document in five bullets."):
    print(token, end="", flush=True)
```

## Project Layout

```text
src/
  cli.py      Interactive terminal chat.
  ingest.py   PDF upload, processing polling, and saved doc_id helpers.
  query.py    DocumentChat wrapper around PageIndex chat completions.
docs/         Local PDFs; ignored by git except docs/.gitkeep.
data/         Generated doc_id and tree JSON files; ignored by git.
```

## Generated Files

The project creates `data/` automatically when `src.ingest` is imported.
Generated records are intentionally ignored by git:

- `data/<pdf-name>.json` stores the document ID returned by PageIndex.
- `data/<pdf-name>_tree.json` stores the processed PageIndex tree.

Keep `data/<pdf-name>.json` if you want to avoid re-uploading a PDF.

## Troubleshooting

If chat says there is no saved document ID, run ingestion first and use the same
PDF filename stem when starting chat.

If upload or chat authentication fails, confirm `.env` contains
`PAGEINDEX_API_KEY` and restart the command.

If a PDF cannot be found, pass a path relative to the project root or an
absolute path.
