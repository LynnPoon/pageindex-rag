import os
import json
import time
from pathlib import Path
from dotenv import load_dotenv
from pageindex import PageIndexClient

load_dotenv()

client = PageIndexClient(api_key=os.getenv("PAGEINDEX_API_KEY"))

DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)


def upload_document(pdf_path: str) -> str:
    """Upload a PDF and return the doc_id. Save it to disk immediately"""
    pdf_path = Path(pdf_path)

    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    print(f"Uploading {pdf_path.name}...")
    # Upload the PDF to PageIndex.
    result = client.submit_document(str(pdf_path))
    # Get the document ID returned by PageIndex.
    doc_id = result["doc_id"]

    # Save so we never lose the doc_id - losing it means re-uploading and spending credits
    record = {"doc_id": doc_id, "filename": pdf_path.name}
    record_path = DATA_DIR / f"{pdf_path.stem}.json"
    record_path.write_text(json.dumps(record, indent=2))

    print(f"Submitted. doc_id: {doc_id}")
    return doc_id


# a function that waits until PageIndex finishes building the tree.
def wait_for_processing(
    doc_id: str, poll_interval: int = 5, timeout: int = 300
) -> dict:
    """Poll every poll_interval seconds until the tree is ready. Returns the full tree."""
    print(f"Building tree for {doc_id}...")
    # Save the start time so we can stop after the timeout.
    start = time.time()

    while True:
        elapsed = time.time() - start
        # Stop if the waiting time is longer than the timeout.
        if elapsed > timeout:
            raise TimeoutError(
                f"Still processing after {timeout}s. Try increasing timeout for large PDFs."
            )

        result = client.get_tree(doc_id)
        status = result.get("status")

        if status == "completed":
            print(f"Done in {elapsed:.0f}s")
            return result

        if status == "failed":
            raise RuntimeError(f"PageIndex failed to process document: {result}")

        print(f"Status: {status}. Waiting {poll_interval}s...")
        time.sleep(poll_interval)


# a helper function that uploads, waits, and saves the tree.
def ingest(pdf_path: str) -> dict:
    """Full pipeline: upload -> wait -> save tree -> return result."""
    doc_id = upload_document(pdf_path)
    tree = wait_for_processing(doc_id)

    # Save the tree locally so you can inspect how PageIndex structured your document
    tree_path = DATA_DIR / f"{Path(pdf_path).stem}_tree.json"
    tree_path.write_text(json.dumps(tree, indent=2))
    print(f"Saved tree to {tree_path}")

    return tree


# a helper function to reload a saved doc_id later.
def load_doc_id(filename_stem: str) -> str:
    """Load a saved doc_id by PDF filename (without extension).
    Example: load_doc_id('report') reads data/report.json"""
    record_path = DATA_DIR / f"{filename_stem}.json"

    if not record_path.exists():
        raise FileNotFoundError(
            f"No saved doc_id for '{filename_stem}'. Run ingest() first."
        )

    record = json.loads(record_path.read_text(encoding="utf-8"))

    return record["doc_id"]
