# PageIndex RAG

A small Python project for uploading PDFs to PageIndex and chatting with them
from the terminal. It saves each uploaded document ID locally so you can ask
questions later without re-uploading the same PDF.

## What It Does

- Uploads a PDF to PageIndex.
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

## Ingest a PDF

Put PDFs under `docs/` or pass any local PDF path. The repository ignores
`docs/*` so local documents are not committed by default.

Run the ingestion helper from Python:

```powershell
uv run python -c "from src.ingest import ingest; ingest('docs/report.pdf')"
```

This creates a local record like:

```text
data/report.json
```

That file stores the PageIndex `doc_id` for `docs/report.pdf`.

## Chat With a PDF

Start the terminal chat:

```powershell
uv run python -m src.cli
```

When prompted, enter the PDF name without `.pdf`. For example, if you ingested
`docs/report.pdf`, enter:

```text
report
```

Then ask questions about the document. Type `exit` or `quit` to stop.

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
