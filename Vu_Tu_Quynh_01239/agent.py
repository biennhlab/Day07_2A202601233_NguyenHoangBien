from typing import Callable

from .store import EmbeddingStore


class KnowledgeBaseAgent:
    """
    RAG agent:
    1. Retrieve relevant chunks.
    2. Build context.
    3. Call the LLM.
    """

    def __init__(
        self,
        store: EmbeddingStore,
        llm_fn: Callable[[str], str],
    ) -> None:
        self.store = store
        self.llm_fn = llm_fn

    def answer(
        self,
        question: str,
        top_k: int = 3,
    ) -> str:
        search_results = self.store.search(
            query=question,
            top_k=top_k,
        )

        if search_results:
            context_parts = []

            for index, result in enumerate(
                search_results,
                start=1,
            ):
                context_parts.append(
                    f"[Nguồn {index}]\n{result['content']}"
                )

            context = "\n\n".join(context_parts)
        else:
            context = "Không tìm thấy thông tin liên quan."

        prompt = f"""
Bạn là trợ lý hỏi đáp dựa trên cơ sở tri thức.

Chỉ sử dụng thông tin trong phần CONTEXT để trả lời.
Nếu CONTEXT không đủ thông tin, hãy nói rõ rằng không tìm
thấy đủ thông tin để trả lời.

CONTEXT:
{context}

QUESTION:
{question}

ANSWER:
""".strip()

        return self.llm_fn(prompt)