# Import sys so we can exit the program safely.
import sys

# Import DocumentChat so we can ask questions.
from src.query import DocumentChat

# Import load_doc_id so we can reuse a saved document ID.
from src.ingest import load_doc_id


def main() -> None:
    print("PageIndex RAG Chat")

    # Ask the user for the PDF filename stem.
    filename_stem = input(
        "Enter saved PDF name without .pdf, for example 'report': "
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

    print("Ask questions about your document.")
    print("Type 'exit' or 'quit' to stop.")

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
