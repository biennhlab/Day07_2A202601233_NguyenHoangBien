"""Benchmark chunkers with metadata-first retrieval and Gemini answers.

Pipeline: metadata filter -> BM25 -> top-3 context -> Gemini -> rubric score.
No embedding model is used.

Run:
    python scripts/benchmark_metadata_chunking.py
    python scripts/benchmark_metadata_chunking.py --no-llm
"""
from __future__ import annotations

import argparse
import math
import os
import re
import statistics
import sys
import time
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from dotenv import load_dotenv
from ingest import load_documents
from src.chunking import (FixedSizeChunker, HeaderChunker, RecursiveChunker,
                          SentenceChunker)

DEFAULT_LLM_MODEL = "gemini-3.1-flash-lite"


class HeaderRecursiveChunker:
    """Split headings first, then recursively split oversized sections."""

    def __init__(self, chunk_size=500):
        self.by_header = HeaderChunker()
        self.recursive = RecursiveChunker(chunk_size=chunk_size)
        self.chunk_size = chunk_size

    def chunk(self, text):
        output = []
        for section in self.by_header.chunk(text):
            output.extend([section] if len(section) <= self.chunk_size
                          else self.recursive.chunk(section))
        return output


# query, metadata filter, groups of acceptable gold-fact patterns
QUESTIONS = (
    ("Trên hệ thống SIS, trạng thái nào xác nhận sinh viên đã đăng ký môn học thành công, trạng thái Selected có ý nghĩa gì và sinh viên kiểm tra lại danh sách môn đã đăng ký ở đâu?",
     {"department": "registrar", "category": "course-registration"},
     (("registered",), ("selected",), ("your class schedule",))),
    ("Sinh viên năm nhất có bắt buộc ở ký túc xá không? Quy định thay đổi thế nào từ năm hai và trường hợp sức khỏe hoặc tôn giáo được xử lý ra sao?",
     {"department": "student-affairs", "category": "dormitory"},
     (("nam nhat",), ("bat buoc",), ("nam hai",), ("khong con la bat buoc",),
      ("suc khoe",), ("ton giao",), ("don de nghi dac cach", "de nghi dac cach"))),
    ("Theo quyền mượn tài liệu thư viện dành cho sinh viên đại học, một sinh viên được mượn tối đa bao nhiêu tài liệu, trong bao lâu và được gia hạn mấy lần?",
     {"department": "library", "category": "library-policies", "audience": "student"},
     (("undergraduate students", "sinh vien dai hoc"), (r"\b3\b",),
      ("2 weeks", "2 tuan"), ("1 time", "1 lan", "gia han 1"))),
    ("VinUni cho phép nộp học phí bằng những hình thức nào và thu học phí vào những thời điểm nào trong năm?",
     {"department": "financial-aid", "category": "tuition-scholarship"},
     (("visa",), ("salesforce",), ("hai dot", "2 dot"),
      ("mua thu",), ("mua xuan",))),
    ("Theo quy trình xét tốt nghiệp, sinh viên thường nộp đơn, được xét ra quyết định và nhận bằng chính thức vào những tháng nào?",
     {"department": "registrar", "category": "academic-services"},
     (("thang 4",), ("thang 8",), ("thang 9",))),
)

STOP = {"bao", "cac", "cho", "co", "cua", "da", "duoc", "gi", "khi",
        "la", "mot", "nao", "nhung", "sinh", "tai", "theo", "trong",
        "tu", "va", "vao", "ve"}


def normalize(text):
    text = unicodedata.normalize("NFD", text.casefold())
    text = "".join(c for c in text if unicodedata.category(c) != "Mn")
    return re.sub(r"\s+", " ", text).strip()


def tokens(text):
    return [x for x in re.findall(r"[a-z0-9]+", normalize(text))
            if len(x) > 1 and x not in STOP]


def bm25(query, chunks):
    """Dependency-free BM25, used only after metadata filtering."""
    docs, terms = [tokens(x) for x in chunks], set(tokens(query))
    if not docs:
        return []
    average, count = statistics.fmean(map(len, docs)) or 1, len(docs)
    frequencies = {term: sum(term in doc for doc in docs) for term in terms}
    output = []
    for doc in docs:
        score = 0.0
        for term in terms:
            frequency = doc.count(term)
            if frequency:
                df = frequencies[term]
                inverse = math.log(1 + (count - df + .5) / (df + .5))
                score += inverse * frequency * 2.5 / (
                    frequency + 1.5 * (.25 + .75 * len(doc) / average)
                )
        output.append(score)
    return output


def coverage(text, facts):
    text = normalize(text)
    return sum(any(re.search(pattern, text) for pattern in alternatives)
               for alternatives in facts) / len(facts)


def search(records, question, top_k=3):
    query, filters, _ = question
    candidates = [record for record in records
                  if all(record["metadata"].get(key) == value
                         for key, value in filters.items())]
    scores = bm25(query, [record["content"] for record in candidates])
    ranked = sorted(zip(scores, candidates),
                    key=lambda pair: (-pair[0], pair[1]["id"]))
    return [record for _, record in ranked[:top_k]], len(candidates)


def create_llm(model_name):
    load_dotenv(ROOT / ".env", override=False)
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is missing from .env or the environment")
    from google import genai
    from google.genai import types
    client = genai.Client(api_key=api_key)
    last_call_at = [0.0]

    def answer(question, chunks):
        context = "\n\n".join(
            f"[Chunk {index}]\n{chunk['content']}"
            for index, chunk in enumerate(chunks, 1)
        )
        prompt = (
            "Bạn là trợ lý RAG. Chỉ trả lời bằng dữ kiện có trong CONTEXT; "
            "không suy đoán. Trả lời ngắn gọn bằng tiếng Việt nhưng phải bao "
            "gồm đủ mọi ý được hỏi. Nếu thiếu thông tin, nói rõ phần bị thiếu.\n\n"
            f"CONTEXT:\n{context}\n\nQUESTION:\n{question}\n\nANSWER:"
        )
        response = None
        for attempt in range(4):
            # Free tier allows 15 requests/minute for this model.
            wait_for = 4.2 - (time.monotonic() - last_call_at[0])
            if wait_for > 0:
                time.sleep(wait_for)
            last_call_at[0] = time.monotonic()
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        temperature=0,
                        max_output_tokens=350,
                    ),
                )
                break
            except Exception as error:
                if "429" not in str(error) or attempt == 3:
                    raise
                time.sleep(6 * (attempt + 1))
        return (response.text or "").strip()

    return answer


def evaluate(name, chunker, documents, llm_answer=None):
    started = time.perf_counter()
    records = []
    for document in documents:
        for index, content in enumerate(chunker.chunk(document.content)):
            records.append({"id": f"{document.id}::{index}", "content": content,
                            "metadata": document.metadata})
    chunk_ms = (time.perf_counter() - started) * 1000
    search_ms = llm_seconds = 0.0
    details, candidate_counts = [], []
    for number, question in enumerate(QUESTIONS, 1):
        started = time.perf_counter()
        top, candidate_count = search(records, question)
        search_ms += (time.perf_counter() - started) * 1000
        candidate_counts.append(candidate_count)
        context_1 = coverage(top[0]["content"] if top else "", question[2])
        context_3 = coverage("\n".join(item["content"] for item in top), question[2])
        answer = ""
        if llm_answer is not None:
            started = time.perf_counter()
            answer = llm_answer(question[0], top)
            llm_seconds += time.perf_counter() - started
        answer_facts = coverage(answer, question[2]) if answer else 0.0
        if llm_answer is None:
            rubric = 2 if context_3 == 1 else int(context_3 > 0)
        else:
            # SCORING.md: 2 only if relevant is top-1 and agent answer is exact.
            rubric = 2 if context_1 > 0 and answer_facts == 1 else int(context_3 > 0)
        details.append({"number": number, "context_1": context_1,
                        "context_3": context_3, "answer_facts": answer_facts,
                        "rubric": rubric, "answer": answer})
    lengths = [len(record["content"]) for record in records]
    return {"name": name, "chunks": len(records),
            "avg": statistics.fmean(lengths), "max": max(lengths),
            "filter": 1-statistics.fmean(candidate_counts)/len(records),
            "context3": statistics.fmean(x["context_3"] for x in details),
            "answer_facts": statistics.fmean(x["answer_facts"] for x in details),
            "answer_full": statistics.fmean(x["answer_facts"] == 1 for x in details),
            "score": sum(x["rubric"] for x in details), "chunk_ms": chunk_ms,
            "search_ms": search_ms, "llm_seconds": llm_seconds,
            "details": details}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default=os.getenv("GEMINI_LLM_MODEL", DEFAULT_LLM_MODEL))
    parser.add_argument("--no-llm", action="store_true",
                        help="Only evaluate retrieved context; do not call Gemini")
    args = parser.parse_args()
    documents = load_documents(ROOT / "data" / "k3_university")
    strategies = {
        "fixed_500_o50": FixedSizeChunker(500, 50),
        "sentence_3": SentenceChunker(3),
        "recursive_500": RecursiveChunker(chunk_size=500),
        "header": HeaderChunker(),
        "header_recursive_500": HeaderRecursiveChunker(500),
    }
    llm_answer = None if args.no_llm else create_llm(args.model)
    results = [evaluate(name, chunker, documents, llm_answer)
               for name, chunker in strategies.items()]
    mode = "context only" if args.no_llm else f"Gemini {args.model}"
    print(f"Corpus: {len(documents)} | Queries: {len(QUESTIONS)} | Mode: {mode}")
    print("Retrieval: metadata filter -> BM25 (NO EMBEDDING)\n")
    print("strategy                 chunks context@3 agent_facts agent_full score search_ms llm_s")
    print("-" * 92)
    for result in results:
        print(f"{result['name']:24} {result['chunks']:6d} "
              f"{result['context3']:9.0%} {result['answer_facts']:11.0%} "
              f"{result['answer_full']:10.0%} {result['score']:2d}/10 "
              f"{result['search_ms']:9.2f} {result['llm_seconds']:5.2f}")
    print("\nPer query: Qn=context@3/agent facts/rubric")
    for result in results:
        detail = ", ".join(
            f"Q{x['number']}={x['context_3']:.0%}/{x['answer_facts']:.0%}/{x['rubric']}"
            for x in result["details"]
        )
        print(f"{result['name']:24} {detail}")
    print("\nAgent answers")
    for result in results:
        print(f"\n[{result['name']}]")
        for detail in result["details"]:
            compact = re.sub(r"\s+", " ", detail["answer"]).strip()
            print(f"Q{detail['number']}: {compact}")
    winner = max(results, key=lambda x: (x["score"], x["answer_facts"],
                                         x["context3"], -x["chunks"]))
    print(f"\nBest: {winner['name']} | {winner['score']}/10 | "
          f"agent_facts={winner['answer_facts']:.0%}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())