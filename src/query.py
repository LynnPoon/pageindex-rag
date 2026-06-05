import os
from typing import Generator
from dotenv import load_dotenv
from pageindex import PageIndexClient

load_dotenv()

client = PageIndexClient(api_key=os.getenv("PAGEINDEX_API_KEY"))


class DocumentChat:
    """All-in-one query engine for a PageIndex document.
    Three ways to get an answer:
    chat.ask(question) -> returns the full answer as a string
    chat.ask_stream(question) -> streams the answer token by token
    chat.ask_stream_with_trace(q) -> streams answer + shows retrieval steps

    All three methods automatically include conversation history, so follow-up questions work correctly without any extra setup.
    """

    def __init__(self, doc_id: str):
        self.doc_id = doc_id
        self.history: list[dict[str, str]] = []

    # Ask one question and wait for the full answer.
    def ask(self, question: str) -> str:
        """Full answer as a single string. Automatically manages history."""
        # Add the user's question to the conversation history.
        self.history.append({"role": "user", "content": question})

        # Send the full conversation history to PageIndex.
        response = client.chat_completions(
            messages=self.history,
            doc_id=self.doc_id,
            enable_citations=True,
        )

        # Extract the answer text from the response.
        answer = response["choices"][0]["message"]["content"]

        # Save the assistant answer so future questions have context.
        self.history.append({"role": "assistant", "content": answer})

        # Return the answer text.
        return answer

    # Ask one question and print the answer as it streams in.
    def ask_stream(self, question: str) -> Generator[str, None, None]:
        # Add the user's question to the conversation history.
        self.history.append({"role": "user", "content": question})

        # Create an empty list to collect streamed answer pieces.
        answer_parts: list[str] = []

        # Ask PageIndex for a streaming response.
        stream = client.chat_completions(
            messages=self.history,
            doc_id=self.doc_id,
            stream=True,
            enable_citations=True,
        )

        # Loop through each streamed chunk.
        for chunk in stream:
            # Convert plain string chunks directly into text.
            if isinstance(chunk, str):
                # Store the text chunk.
                answer_parts.append(chunk)

                # Send the text chunk back to the caller.
                yield chunk

            # Handle dictionary chunks if the SDK returns OpenAI-style streaming data.
            elif isinstance(chunk, dict):
                # Safely get the streamed text from the dictionary.
                content = (
                    chunk.get("choices", [{}])[0].get("delta", {}).get("content", "")
                )

                # Only handle non-empty content.
                if content:
                    # Store the content chunk.
                    answer_parts.append(content)

                    # Send the content chunk back to the caller.
                    yield content

        # Join all streamed chunks into one final answer.
        full_answer = "".join(answer_parts)

        # Save the assistant answer to history.
        self.history.append({"role": "assistant", "content": full_answer})

    # Ask one question and show retrieval/tool trace metadata while streaming.
    def ask_stream_with_trace(self, question: str) -> Generator[str, None, None]:
        # Add the user's question to the conversation history.
        self.history.append({"role": "user", "content": question})

        # Create an empty list to collect answer chunks.
        answer_parts: list[str] = []

        # Ask PageIndex for streaming chunks with metadata.
        stream = client.chat_completions(
            messages=self.history,
            doc_id=self.doc_id,
            stream=True,
            stream_metadata=True,
            enable_citations=True,
        )

        # Loop through each streamed chunk.
        for chunk in stream:
            # Skip non-dictionary chunks because metadata needs dictionary format.
            if not isinstance(chunk, dict):
                # Store plain text chunks.
                answer_parts.append(chunk)

                # Send the plain text chunk back.
                yield chunk

                # Continue to the next chunk.
                continue

            # Get metadata about PageIndex retrieval steps.
            metadata = chunk.get("block_metadata", {})

            # Check whether metadata exists.
            if metadata:
                # Get the type of internal retrieval step.
                block_type = metadata.get("type")

                # Show when PageIndex starts searching the document.
                if block_type == "mcp_tool_use_start":
                    # Yield a readable trace message.
                    yield "\n[Searching document...]\n"

                # Show when PageIndex has retrieved relevant content.
                elif block_type == "mcp_tool_result_start":
                    # Yield a readable trace message.
                    yield "\n[Retrieved relevant content...]\n"

            # Get the answer text from the chunk.
            content = chunk.get("choices", [{}])[0].get("delta", {}).get("content", "")

            # Only handle non-empty answer text.
            if content:
                # Store the answer text.
                answer_parts.append(content)

                # Send the answer text back.
                yield content

        # Join all collected answer text.
        full_answer = "".join(answer_parts)

        # Save the answer to conversation history.
        self.history.append({"role": "assistant", "content": full_answer})
