import os
import uuid

from dotenv import load_dotenv
from langchain_core.documents import Document
from langchain_core.tools import tool
from langchain_openrouter import ChatOpenRouter
from langsmith import traceable


load_dotenv()


model = ChatOpenRouter(
    model=os.getenv("MODEL_NAME"),
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url=os.getenv("BASE_URL"),
    temperature=0,
    timeout=30_000,
)

documents = [
    Document(
        page_content=(
            "LangSmith provides tracing and observability "
            "for LLM applications."
        )
    ),
    Document(
        page_content=(
            "LangChain is a framework for building "
            "applications powered by language models."
        )
    ),
]


@traceable(
    name="retrieve_documents",
    run_type="retriever"
)
def retrieve_documents(query: str):
    query_words = query.lower().split()

    results = [doc for doc in documents
        if any(word in doc.page_content.lower()
            for word in query_words)
    ]

    return results[:2]

@tool
def word_count(text: str) -> int:
    """Count the number of words in the supplied text."""

    return len(text.split())

@traceable(name="observability_request")
def run_request(question: str, request_id: str) -> str:

    retrieved_docs = retrieve_documents(
        question,
        langsmith_extra={"metadata": {
                "request_id": request_id
            }
        },
    )

    context = "\n".join(doc.page_content for doc in retrieved_docs)

    config = {
        "metadata": {
            "request_id": request_id
        },
        "tags": [ "observability","task2","tracing"],
    }

    count = word_count.invoke( {"text": context},config=config,)

    prompt = f"""
Use the following context to answer the question.

Context:
{context}

Context word count: {count}

Question:
{question}

Answer in one short sentence.
"""

    response = model.invoke(prompt,config=config)

    return response.content

def main():
    request_id = str(uuid.uuid4())[:8]

    print("Correlation ID:", request_id)

    answer = run_request("What does LangSmith provide?",request_id,
        langsmith_extra={
            "metadata": {"request_id": request_id}})

    print("\nAnswer:")
    print(answer)


if __name__ == "__main__":
    main()