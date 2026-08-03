# Báo Cáo Cá Nhân — Lab 7: Embedding & Vector Store

**Họ tên:** Nguyễn Hoàng Biên
**Nhóm:** DMX
**Ngày:** 03/08/2026

> **Nộp 1 bản / sinh viên.** Phần nhóm (lựa chọn tài liệu, thiết kế chiến lược, bộ câu hỏi đánh giá, demo) nộp chung 1 bản trong `REPORT_NHOM.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần cá nhân: 60** = Khởi động (5) + Hướng tiếp cận (10) + Hoàn thiện code (30) + Dự đoán độ tương tự (5) + Kết quả truy xuất của tôi (10).

---

## 1. Khởi động (Warm-up) — Cá nhân (5 điểm)

### Độ tương tự Cosine (Cosine Similarity) (Bài tập 1.1)

**Độ tương tự cosine cao (High cosine similarity) nghĩa là gì?**

> độ tương tự cao có nghĩa là các chunk có ngữ nghĩa gần giống nhau các vector sau khi embbed có góc rất nhỏ nên phân bố sẽ gần nhau hơn

**Ví dụ có độ tương tự CAO:**

- Câu A: con chó ăn xương
- Câu B: con mèo ăn cá
- Tại sao tương đồng: vì chó và mèo đều trong cùng 1 domain động vật nên độ tương đồng cao

**Ví dụ có độ tương tự THẤP:**

- Câu A: con mèo ăn cá
- Câu B: xe máy chạy nhanh
- Tại sao khác: vì con mèo và xe máy khác domain (sinh học và cơ khí giao thông) nên độ tương đồng thấp và góc của 2 vector đại diện sẽ lớn nên phân bố của 2 vector này sẽ xa nhau hơn

**Tại sao độ tương tự cosine (cosine similarity) được ưu tiên hơn khoảng cách Euclid (Euclidean distance) cho text embeddings?**

> bởi vì cosine similarity nó không bị phụ thuộc vào độ dài của chunk mà nó phụ thuộc và ngữ nghĩa của chunk nên khi 2 câu cùng nói về con chó dù dộ dài nó có khác biệt lớn thì vector đại diện của 2 câu này vẫn sẽ có góc rất nhỏ. Ngược lại thì edulidean distance sẽ có góc rất lớn đối với 2 câu trên.

### Bài toán tính toán Chunking (Bài tập 1.2)

**Tài liệu 10,000 ký tự, chunk_size=500, overlap=50. Bao nhiêu chunks?**

> chunk_size=500, overlap=50 => step = 500 - 50 = 450.
> số chunk = [10000 - 500 / 450] + 1 = 23
> *Đáp án:* 23

**Nếu độ chồng chéo (overlap) tăng lên 100, số lượng chunk thay đổi thế nào? Tại sao muốn độ chồng chéo nhiều hơn?**

> nếu overlap tăng lên 100 thì step sẽ giảm xuống 400 dẫn đến số lượng chunk nhiều hơn. Muốn độ chồng chéo nhiều hơn vì nó sẽ khiến cho các chunk sau sẽ giữ lại context của các chunk trước nhiều hơn và llm không bị mất thông tin và có thể sinh ra câu trả lời hiệu quả hơn

---

## 2. Hướng tiếp cận của tôi (My Approach) — Cá nhân (10 điểm)

Giải thích cách tiếp cận của bạn khi lập trình (implement) các phần chính trong gói `src`.

### Các hàm chia nhỏ (Chunking Functions)

**`SentenceChunker.chunk`** — hướng tiếp cận:

> Sử dụng biểu thức chính quy `(?<=[.!?])\s+|\.\n` (kết hợp lookbehind) để cắt câu mà vẫn giữ lại được dấu kết thúc. Các ngoại lệ như đầu vào rỗng (empty string) hoặc chứa khoảng trắng thừa được xử lý gọn gàng bằng lệnh kiểm tra if ngay từ đầu và hàm `strip()` trước khi gom các câu thành chunk.

**`RecursiveChunker.chunk` / `_split`** — hướng tiếp cận:

> Thuật toán đệ quy cắt văn bản dựa trên danh sách dấu phân cách có mức độ ưu tiên giảm dần (từ đoạn văn `\n\n` xuống khoảng trắng `" "`). Base case (trường hợp cơ sở) để dừng đệ quy là khi văn bản đã ngắn hơn `chunk_size`, hoặc khi đã hết danh sách dấu phân cách mà đoạn vẫn quá dài (lúc này tiến hành cắt cứng - hard slice).

### Lớp EmbeddingStore

**`add_documents` + `search`** — hướng tiếp cận:

> Các tài liệu được embedding và lưu song song: đẩy vào collection của ChromaDB (nếu khả dụng) hoặc lưu in-memory dưới dạng List of Dicts. Khi tìm kiếm, vector của query sẽ được tính Cosine Similarity (hoặc truy vấn trực tiếp qua ChromaDB) với từng record để trả về danh sách top-K các chunk có độ tương tự giảm dần.

**`search_with_filter` + `delete_document`** — hướng tiếp cận:

> Việc lọc (filter) qua metadata luôn được thực hiện TRƯỚC để tối ưu không gian tìm kiếm, sau đó mới tính độ tương tự trên tập kết quả thu gọn. Khi xóa, tôi dùng list comprehension (hoặc API của ChromaDB) để duyệt và loại bỏ tất cả các bản ghi có chứa `doc_id` hoặc `id` trùng khớp.

### Tác tử KnowledgeBaseAgent

**`answer`** — hướng tiếp cận:

> Hàm gọi tới store để lấy top-K chunk liên quan nhất. Ngữ cảnh (context) được đưa vào prompt bằng cách nối chuỗi (join) các đoạn text tìm được, kèm theo phần định hướng LLM rõ ràng kiểu: "Dựa vào ngữ cảnh dưới đây... Hãy trả lời câu hỏi sau...".

---

## 3. Hoàn thiện code (Core Implementation) — Cá nhân (30 điểm)

Vượt qua bộ kiểm thử là điều kiện tính điểm phần này.

### Kết Quả Kiểm Thử (Test Results)

```
============================= test session starts =============================
platform win32 -- Python 3.13.9, pytest-8.4.2, pluggy-1.5.0 -- C:\Users\thinkpad\miniconda3\python.exe
cachedir: .pytest_cache
rootdir: D:\VinUni\lab\Day07_2A202601233_NguyenHoangBien
plugins: anyio-4.12.0, langsmith-0.5.2, asyncio-0.26.0
asyncio: mode=Mode.STRICT, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collecting ... collected 42 items

tests/test_solution.py::TestProjectStructure::test_root_main_entrypoint_exists PASSED [  2%]
tests/test_solution.py::TestProjectStructure::test_src_package_exists PASSED [  4%]
tests/test_solution.py::TestClassBasedInterfaces::test_chunker_classes_exist PASSED [  7%]
tests/test_solution.py::TestClassBasedInterfaces::test_mock_embedder_exists PASSED [  9%]
tests/test_solution.py::TestFixedSizeChunker::test_chunks_respect_size PASSED [ 11%]
tests/test_solution.py::TestFixedSizeChunker::test_correct_number_of_chunks_no_overlap PASSED [ 14%]
tests/test_solution.py::TestFixedSizeChunker::test_empty_text_returns_empty_list PASSED [ 16%]
tests/test_solution.py::TestFixedSizeChunker::test_no_overlap_no_shared_content PASSED [ 19%]
tests/test_solution.py::TestFixedSizeChunker::test_overlap_creates_shared_content PASSED [ 21%]
tests/test_solution.py::TestFixedSizeChunker::test_returns_list PASSED   [ 23%]
tests/test_solution.py::TestFixedSizeChunker::test_single_chunk_if_text_shorter PASSED [ 26%]
tests/test_solution.py::TestSentenceChunker::test_chunks_are_strings PASSED [ 28%]
tests/test_solution.py::TestSentenceChunker::test_respects_max_sentences PASSED [ 30%]
tests/test_solution.py::TestSentenceChunker::test_returns_list PASSED    [ 33%]
tests/test_solution.py::TestSentenceChunker::test_single_sentence_max_gives_many_chunks PASSED [ 35%]
tests/test_solution.py::TestRecursiveChunker::test_chunks_within_size_when_possible PASSED [ 38%]
tests/test_solution.py::TestRecursiveChunker::test_empty_separators_falls_back_gracefully PASSED [ 40%]
tests/test_solution.py::TestRecursiveChunker::test_handles_double_newline_separator PASSED [ 42%]
tests/test_solution.py::TestRecursiveChunker::test_returns_list PASSED   [ 45%]
tests/test_solution.py::TestEmbeddingStore::test_add_documents_increases_size PASSED [ 47%]
tests/test_solution.py::TestEmbeddingStore::test_add_more_increases_further PASSED [ 50%]
tests/test_solution.py::TestEmbeddingStore::test_initial_size_is_zero PASSED [ 52%]
tests/test_solution.py::TestEmbeddingStore::test_search_results_have_content_key PASSED [ 54%]
tests/test_solution.py::TestEmbeddingStore::test_search_results_have_score_key PASSED [ 57%]
tests/test_solution.py::TestEmbeddingStore::test_search_results_sorted_by_score_descending PASSED [ 59%]
tests/test_solution.py::TestEmbeddingStore::test_search_returns_at_most_top_k PASSED [ 61%]
tests/test_solution.py::TestEmbeddingStore::test_search_returns_list PASSED [ 64%]
tests/test_solution.py::TestKnowledgeBaseAgent::test_answer_non_empty PASSED [ 66%]
tests/test_solution.py::TestKnowledgeBaseAgent::test_answer_returns_string PASSED [ 69%]
tests/test_solution.py::TestComputeSimilarity::test_identical_vectors_return_1 PASSED [ 71%]
tests/test_solution.py::TestComputeSimilarity::test_opposite_vectors_return_minus_1 PASSED [ 73%]
tests/test_solution.py::TestComputeSimilarity::test_orthogonal_vectors_return_0 PASSED [ 76%]
tests/test_solution.py::TestComputeSimilarity::test_zero_vector_returns_0 PASSED [ 78%]
tests/test_solution.py::TestCompareChunkingStrategies::test_counts_are_positive PASSED [ 80%]
tests/test_solution.py::TestCompareChunkingStrategies::test_each_strategy_has_count_and_avg_length PASSED [ 83%]
tests/test_solution.py::TestCompareChunkingStrategies::test_returns_three_strategies PASSED [ 85%]
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_filter_by_department PASSED [ 88%]
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_no_filter_returns_all_candidates PASSED [ 90%]
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_returns_at_most_top_k PASSED [ 92%]
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_reduces_collection_size PASSED [ 95%]
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_returns_false_for_nonexistent_doc PASSED [ 97%]
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_returns_true_for_existing_doc PASSED [100%]

============================= 42 passed in 0.08s ==============================
```

**Số lượng bài test vượt qua (pass):** 42 / 42

---

## 4. Dự đoán độ tương tự (Similarity Predictions) — Cá nhân (5 điểm)

| Cặp | Câu A                                               | Câu B                                                       | Dự đoán | Điểm thực tế | Đúng? |
| ---- | ---------------------------------------------------- | ------------------------------------------------------------ | ---------- | ---------------- | ------- |
| 1    | "Sinh viên có thể mượn tối đa 5 cuốn sách." | "Quy định thư viện cho phép mượn 5 tài liệu."       | Cao        | ~0.92            | Đúng  |
| 2    | "Đăng ký môn học bắt đầu từ ngày 1/8."     | "Hôm nay thời tiết Hà Nội rất đẹp."                  | Thấp      | ~0.08            | Đúng  |
| 3    | "Sinh viên phải đóng học phí trước 15/9."    | "Hạn chót thanh toán học phí là 15 tháng 9."          | Cao        | ~0.95            | Đúng  |
| 4    | "VinUni yêu cầu sinh viên năm nhất ở KTX."     | "KTX VinUni có điều hòa và máy giặt."                 | Thấp      | ~0.55            | Đúng  |
| 5    | "Tôi muốn hủy đăng ký môn Cơ sở Dữ liệu." | "Sinh viên rút môn Database Foundation phải làm đơn." | Cao        | ~0.84            | Đúng  |

**Kết quả nào bất ngờ nhất? Điều này nói gì về cách embeddings biểu diễn ý nghĩa?**

> Kết quả bất ngờ nhất là cặp số 4. Dù có chung nhiều từ khóa (KTX, VinUni), điểm tương đồng lại khá thấp vì mô hình embedding hiểu được khác biệt về mặt ngữ nghĩa: một bên là "quy định bắt buộc", bên kia là "cơ sở vật chất". Điều này chứng tỏ embedding lưu giữ ý nghĩa thực sự của câu (semantic) chứ không chỉ đơn thuần là đếm từ khóa (keyword matching).

---

## 5. Kết quả truy xuất của tôi (Competition Results) — Cá nhân (10 điểm)

Chạy **5 câu hỏi đánh giá của nhóm** trên mã nguồn cá nhân của bạn trong gói `src`. **5 câu hỏi này phải trùng với các thành viên cùng nhóm** (xem `REPORT_NHOM.md`).

| # | Câu hỏi benchmark của nhóm | Top-1 chunk (tóm tắt) | BM25 | Top-3 liên quan? | Câu trả lời Agent (tóm tắt) | Điểm rubric |
| ---: | --- | --- | ---: | :---: | --- | ---: |
| 1 | Trên hệ thống SIS, trạng thái nào xác nhận sinh viên đã đăng ký môn học thành công, trạng thái “Selected” có ý nghĩa gì và sinh viên kiểm tra lại danh sách môn đã đăng ký ở đâu? | `dangkymonhoc::7` — phần thêm môn, đăng ký và xác nhận lịch học | 17.8145 | Có | Trả lời đủ: trạng thái `Registered`; `Selected` là chưa đăng ký thành công; kiểm tra tại `Your Class Schedule`. | 2/2 |
| 2 | Sinh viên năm nhất có bắt buộc ở ký túc xá không? Quy định thay đổi thế nào từ năm hai và trường hợp sức khỏe hoặc tôn giáo được xử lý ra sao? | `ktx::2` — quy định ở KTX theo năm học và trường hợp đặc cách | 29.0290 | Có | Nêu đúng phần lớn quy định năm nhất, năm hai và ngoại lệ sức khỏe/tôn giáo, nhưng còn thiếu một dữ kiện/diễn đạt chuẩn trong gold answer. | 1/2 |
| 3 | Theo quyền mượn tài liệu thư viện dành cho sinh viên đại học, một sinh viên được mượn tối đa bao nhiêu tài liệu, trong bao lâu và được gia hạn mấy lần? | `thuvien::21` — quy định sử dụng tài nguyên điện tử, không phải bảng quyền mượn | 1.8209 | Không | Context không chứa các dữ kiện “3 tài liệu, 2 tuần, gia hạn 1 lần”, nên Agent không thể trả lời đúng. | 0/2 |
| 4 | VinUni cho phép nộp học phí bằng những hình thức nào và thu học phí vào những thời điểm nào trong năm? | `hocphi_hocbong::3` — hình thức nộp học phí | 13.8901 | Có | Nêu được phần lớn thông tin Visa, Salesforce và kỳ thu học phí, nhưng chưa đủ toàn bộ dữ kiện chuẩn. | 1/2 |
| 5 | Theo quy trình xét tốt nghiệp, sinh viên thường nộp đơn, được xét ra quyết định và nhận bằng chính thức vào những tháng nào? | `totnghiep::5` — thời gian và quy trình xét tốt nghiệp | 20.3940 | Có | Trả lời đủ: nộp đơn tháng 4, xét và ra quyết định tháng 8, nhận bằng tháng 9. | 2/2 |

**Tổng điểm theo `docs/SCORING.md`: 6/10.**

- Có chunk liên quan trong Top-3: **4/5 câu**.
- Agent trả lời đầy đủ gold answer: **2/5 câu** (Q1 và Q5).
- Độ phủ dữ kiện trung bình trong Top-3: **73%**.
- Độ phủ dữ kiện trung bình trong Agent Answer: **73%**.

**Failure case chính:** Q3. Metadata filter đưa truy vấn vào đúng tài liệu `thuvien.md`, nhưng BM25 xếp section tài nguyên điện tử cao hơn bảng `Circulation Privileges`. Nguyên nhân là query tiếng Việt trong khi bảng dùng các cụm tiếng Anh như `Undergraduate Students`, `2 weeks` và `1 time`.

**Điều hay nhất tôi học được từ các thành viên khác:** Fixed Size có overlap giữ dữ kiện bảng tốt hơn ở Q3, trong khi Recursive thuần đạt chất lượng tổng thể cao hơn Header+Recursive một chút. Với tài liệu song ngữ hoặc bảng Markdown, chỉ tách theo heading chưa đủ; cần bổ sung metadata song ngữ, lặp heading trong chunk con hoặc chuẩn hóa bảng thành câu văn dễ tìm kiếm.

---

## Tự Đánh Giá (Phần Cá Nhân)

| Tiêu chí                                           | Điểm tự đánh giá |
| ---------------------------------------------------- | ---------------------- |
| Khởi động (Warm-up)                               | 5 / 5                  |
| Hướng tiếp cận của tôi (My Approach)           | 10 / 10                |
| Hoàn thiện code (Core Implementation — tests)     | 24 / 30                |
| Dự đoán độ tương tự (Similarity Predictions) | 5 / 5                  |
| Kết quả truy xuất của tôi (Competition Results) | 6 / 10                 |
| **Tổng phần cá nhân**                      | **50 / 60**      |
