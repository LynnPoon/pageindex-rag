# Import sys so we can exit the program safely.
import sys

# Import DocumentChat so we can ask questions.
from src.query import DocumentChat

# Import load_doc_id so we can reuse a saved document ID.
from src.ingest import load_doc_id, ingest


def main() -> None:
    print("=" * 32)
    print("  PageIndex Document Assistant")
    print("=" * 32)

    pdf_path = (
        input("\nEnter the path to a new PDF, or press Enter to use a saved PDF: ")
        .strip()
        .strip('"')
    )

    if pdf_path:
        ingest(pdf_path)

    # Ask the user for the ingested PDF file to chat with.
    filename_stem = input(
        "Enter the name of the saved PDF (without the .pdf extension): "
    ).strip()

    # Try to load the saved doc_id.
    try:
        # Load the doc_id from data/<filename_stem>.json.
        doc_id = load_doc_id(filename_stem)

    # Catch the error if the saved doc_id file does not exist.
    except FileNotFoundError as error:
        print(error)

        # Exit the program.
        sys.exit(1)

    # Create a chat object for this document.
    chat = DocumentChat(doc_id)

    print("\nAssistant: Your document is ready. Ask me anything about it.")
    print("Type 'exit' or 'quit' to end the session.")

    while True:
        question = input("\nYou: ").strip()

        # Skip empty questions.
        if not question:
            continue

        if question.lower() in {"exit", "quit"}:
            print("Goodbye!")
            break
        print("\nAssistant: ", end="", flush=True)

        # Stream the answer chunk by chunk.
        for token in chat.ask_stream(question):
            # Print each token immediately.
            print(token, end="", flush=True)

        # Print a final new line.
        print()


if __name__ == "__main__":
    main()
