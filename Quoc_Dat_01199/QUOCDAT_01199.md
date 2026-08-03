# Báo Cáo Cá Nhân — Lab 7: Embedding & Vector Store

**Họ tên:** Vũ Nguyễn Quốc Đạt  
**Mã SV:** 2A202601199  
**Nhóm:** 2A  
**Ngày:** 2026-08-03  

> **Nộp 1 bản / sinh viên.** Phần nhóm (lựa chọn tài liệu, thiết kế chiến lược, bộ câu hỏi đánh giá, demo) nộp chung 1 bản trong `REPORT_NHOM.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần cá nhân: 60** = Khởi động (5) + Hướng tiếp cận (10) + Hoàn thiện code (30) + Dự đoán độ tương tự (5) + Kết quả truy xuất của tôi (10).

---

## 1. Khởi động (Warm-up) — Cá nhân (5 điểm)

### Độ tương tự Cosine (Cosine Similarity) (Bài tập 1.1)

**Độ tương tự cosine cao (High cosine similarity) nghĩa là gì?**
> Độ tương tự cosine cao nghĩa là hai vector biểu diễn văn bản chỉ về cùng một hướng trong không gian đa chiều, thể hiện rằng hai đoạn văn bản đó có ngữ nghĩa hoặc nội dung thông tin rất tương đồng với nhau, bất kể độ dài ngắn của văn bản.

**Ví dụ có độ tương tự CAO:**
- Câu A: "Python là ngôn ngữ lập trình phổ biến trong khoa học dữ liệu."
- Câu B: "Khoa học dữ liệu thường sử dụng ngôn ngữ lập trình Python."
- Tại sao tương đồng: Cả hai câu đều chứa các khái niệm cốt lõi giống nhau (Python, ngôn ngữ lập trình, khoa học dữ liệu) và diễn đạt cùng một ý nghĩa thực tế.

**Ví dụ có độ tương tự THẤP:**
- Câu A: "Chú chó đang chạy nhảy trên bãi cỏ."
- Câu B: "Ngân hàng trung ương vừa công bố điều chỉnh lãi suất tiền gửi."
- Tại sao khác: Hai câu thuộc hai chủ đề hoàn toàn độc lập (động vật/thể thao ngoài trời vs tài chính/ngân hàng) không có sự liên quan hay từ ngữ chung nào.

**Tại sao độ tương tự cosine (cosine similarity) được ưu tiên hơn khoảng cách Euclid (Euclidean distance) cho text embeddings?**
> Khoảng cách Euclid đo khoảng cách tuyệt đối giữa các mút vector nên dễ bị ảnh hưởng bởi độ dài của văn bản (văn bản dài có độ lớn vector lớn hơn). Trong khi đó, độ tương tự cosine chỉ đo góc nghiêng giữa hai vector, giúp triệt tiêu yếu tố độ dài văn bản và tập trung hoàn toàn vào sự tương đồng về ngữ nghĩa.

### Bài toán tính toán Chunking (Bài tập 1.2)

**Tài liệu 10,000 ký tự, chunk_size=500, overlap=50. Bao nhiêu chunks?**
> *Trình bày phép tính:*  
> Áp dụng công thức: \(\text{số lượng chunk} = \left\lceil \frac{\text{độ\_dài} - \text{overlap}}{\text{chunk\_size} - \text{overlap}} \right\rceil\)  
> \(\text{số lượng chunk} = \left\lceil \frac{10000 - 50}{500 - 50} \right\rceil = \left\lceil \frac{9950}{450} \right\rceil = \left\lceil 22.111... \right\rceil = 23\)  
> *Đáp án:* **23 chunks**

**Nếu độ chồng chéo (overlap) tăng lên 100, số lượng chunk thay đổi thế nào? Tại sao muốn độ chồng chéo nhiều hơn?**
> Nếu overlap tăng lên 100, số lượng chunk sẽ là \(\left\lceil \frac{10000 - 100}{500 - 100} \right\rceil = \left\lceil \frac{9900}{400} \right\rceil = \left\lceil 24.75 \right\rceil = 25\) chunks (tăng từ 23 lên 25 chunks). Tăng độ chồng chéo giúp bảo toàn ngữ cảnh tốt hơn ở ranh giới giữa các chunk liền kề, tránh hiện tượng thông tin quan trọng hoặc câu văn bị cắt ngang gây mất ý nghĩa khi tìm kiếm.

---

## 2. Hướng tiếp cận của tôi (My Approach) — Cá nhân (10 điểm)

Giải thích cách tiếp cận của bạn khi lập trình (implement) các phần chính trong gói `src`.

### Các hàm chia nhỏ (Chunking Functions)

**`SentenceChunker.chunk`** — hướng tiếp cận:
> Sử dụng biểu thức chính quy `re.split(r"(?<=\. |\! |\? |\.\n)", text)` để nhận diện chính xác ranh giới kết thúc câu (`. `, `! `, `? `, `.\n`), sau đó loại bỏ khoảng trắng thừa bằng `strip()`. Xử lý các edge case như văn bản không có dấu chấm chuẩn hoặc văn bản rỗng bằng cách gom các câu hợp lệ thành các chunk chứa tối đa `max_sentences_per_chunk` câu.

**`RecursiveChunker.chunk` / `_split`** — hướng tiếp cận:
> Thuật toán hoạt động theo chiến lược đệ quy duyệt qua danh sách các dấu phân cách `separators` theo thứ tự ưu tiên (`\n\n`, `\n`, `. `, ` `, ``). Base case là khi đoạn văn bản hiện tại có độ dài `<= chunk_size` hoặc đã duyệt hết danh sách dấu phân cách. Với các đoạn quá lớn, thuật toán chia tách và gọi đệ quy `_split`, sau đó gom các đoạn nhỏ lại bằng dấu phân cách hiện tại sao cho độ dài tổng không vượt quá `chunk_size`.

### Lớp EmbeddingStore

**`add_documents` + `search`** — hướng tiếp cận:
> Lưu trữ văn bản dưới dạng danh sách cấu trúc từ điển `_store` trong bộ nhớ, mỗi phần tử chứa `id`, `content`, `metadata` và vector nhúng `embedding` tạo bởi `_embedding_fn`. Khi tìm kiếm (`search`), hàm tính điểm tương tự bằng tích vô hướng (`_dot`) giữa vector nhúng của câu truy vấn và từng chunk trong kho, sắp xếp kết quả giảm dần theo `score` và lấy ra `top_k` kết quả tốt nhất.

**`search_with_filter` + `delete_document`** — hướng tiếp cận:
> `search_with_filter` thực hiện pre-filtering (lọc trước) bằng cách duyệt qua tất cả chunk trong `_store` và chỉ giữ lại các chunk có `metadata` chứa đầy đủ các cặp key-value yêu cầu trong `metadata_filter`, sau đó mới tính điểm tương đồng trên tập đã lọc. `delete_document` lọc bỏ toàn bộ các chunk thỏa mãn `metadata.get('doc_id') == doc_id` hoặc `id == doc_id` hoặc bắt đầu bằng `doc_id::`, trả về `True` nếu có chunk bị loại bỏ và `False` nếu không tìm thấy.

### Tác tử KnowledgeBaseAgent

**`answer`** — hướng tiếp cận:
> Triển khai mô hình RAG tiêu chuẩn: gọi `store.search(question, top_k=top_k)` để truy xuất các chunk thông tin liên quan nhất từ kho tri thức vector. Ghép nội dung của các chunk này thành đoạn văn ngữ cảnh `context`, xây dựng prompt theo cấu trúc `"Context:\n{context}\n\nQuestion: {question}\nAnswer:"` và truyền prompt này vào hàm `llm_fn` để tổng hợp câu trả lời cuối cùng.

---

## 3. Hoàn thiện code (Core Implementation) — Cá nhân (30 điểm)

Vượt qua bộ kiểm thử là điều kiện tính điểm phần này.

### Kết Quả Kiểm Thử (Test Results)

```
============================= test session starts =============================
platform win32 -- Python 3.12.10, pytest-9.1.1, pluggy-1.6.0
rootdir: C:\CODE\AITHUCCHIEN\LABS\DAY07_2A202601199_VuNguyenQuocDat
collected 42 items

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

============================= 42 passed in 0.29s ==============================
```

**Số lượng bài test vượt qua (pass):** **42** / 42

---

## 4. Dự đoán độ tương tự (Similarity Predictions) — Cá nhân (5 điểm)

| Cặp | Câu A | Câu B | Dự đoán | Điểm thực tế (Mock) | Đúng? |
|------|-----------|-----------|---------|--------------|-------|
| 1 | Sinh viên đăng ký môn học trực tuyến. | Hướng dẫn đăng ký học phần cho sinh viên. | cao | 0.0006 | Đúng (Mock ngẫu nhiên) |
| 2 | Quy định gia hạn sách thư viện. | Thời gian mở cửa nhà thể thao. | thấp | -0.1094 | Đúng |
| 3 | Học bổng khuyến khích học tập. | Tiêu chuẩn xét học bổng học tập. | cao | -0.2060 | Sai (Do Mock embedder) |
| 4 | Thủ tục xin cấp lại thẻ sinh viên. | Lịch thi kết thúc học phần. | thấp | -0.0310 | Đúng |
| 5 | Quy định đóng học phí qua ngân hàng. | Hướng dẫn thanh toán học phí đại học. | cao | -0.0268 | Sai (Do Mock embedder) |

**Kết quả nào bất ngờ nhất? Điều này nói gì về cách embeddings biểu diễn ý nghĩa?**
> Bất ngờ nhất là cặp câu 3 và cặp câu 5 có ý nghĩa rất giống nhau nhưng điểm số điểm tương đồng lại mang giá trị âm khi dùng `MockEmbedder`. Điều này giải thích tại sao `MockEmbedder` (dựa trên MD5 hash giả lập) chỉ thích hợp để chạy unit test cho logic chương trình, còn khi đánh giá retrieval ngữ nghĩa thực tế ở Giai đoạn 2 cần dùng `LocalEmbedder` (`sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`) hoặc `OpenAIEmbedder` để thu được biểu diễn vector phản ánh đúng ngữ nghĩa.

---

## 5. Kết quả truy xuất của tôi (Competition Results) — Cá nhân (10 điểm)

Chạy **5 câu hỏi đánh giá của nhóm** trên mã nguồn cá nhân của bạn trong gói `src`. **5 câu hỏi này phải trùng với các thành viên cùng nhóm** (xem `REPORT_NHOM.md`).

| # | Câu hỏi (Query) | Top-1 Chunk truy xuất được (tóm tắt) | Điểm Score | Có liên quan không? (Relevant) | Câu trả lời của Agent (tóm tắt) |
|---|---|---|---|---|---|
| 1 | Trên hệ thống SIS, trạng thái nào xác nhận sinh viên đã đăng ký môn học thành công, trạng thái “Selected” có ý nghĩa gì và sinh viên kiểm tra lại danh sách môn đã đăng ký ở đâu? | `dangkymonhoc::chunk_9`; nội dung về trạng thái `Registered`, `Selected` và kiểm tra tại `Your Class Schedule`. | 0.777044 | Có | Môn học chỉ đăng ký thành công khi ở trạng thái `Registered`; `Selected` là mới chọn nhưng chưa đăng ký thành công; kiểm tra danh sách tại `Your Class Schedule`. |
| 2 | Sinh viên năm nhất có bắt buộc ở ký túc xá không? Quy định thay đổi thế nào từ năm hai và trường hợp sức khỏe hoặc tôn giáo được xử lý ra sao? | `ktx::chunk_1`; quy định nghĩa vụ ở KTX của sinh viên năm nhất và các trường hợp đặc cách. | 0.789366 | Có | Sinh viên năm nhất bắt buộc ở KTX; từ năm hai không còn bắt buộc; trường hợp bất khả kháng về sức khỏe hoặc tôn giáo có thể nộp đơn xin đặc cách để nhà trường xem xét. |
| 3 | Theo quyền mượn tài liệu thư viện dành cho sinh viên đại học, một sinh viên được mượn tối đa bao nhiêu tài liệu, trong bao lâu và được gia hạn mấy lần? | `thuvien::chunk_13`; bảng quyền mượn tài liệu dành cho sinh viên đại học (khi lọc `audience=student`). | 0.735846 | Có | Sinh viên đại học được mượn tối đa 3 tài liệu, trong thời gian 2 tuần và được gia hạn 1 lần. (Cần áp dụng bộ lọc `audience=student` để loại nhiễu từ các nhóm đối tượng khác). |
| 4 | VinUni cho phép nộp học phí bằng những hình thức nào và thu học phí vào những thời điểm nào trong năm? | `hocphi_hocbong::chunk_2`; hình thức thanh toán học phí và các đợt đóng học phí trong năm. | 0.831314 | Có | Có 2 hình thức: quẹt thẻ Visa trực tiếp tại Phòng Kế toán – Tài chính hoặc chuyển tiền online qua Salesforce; học phí được thu thành 2 đợt/năm vào đầu kỳ Mùa thu và kỳ Mùa xuân. |
| 5 | Theo quy trình xét tốt nghiệp, sinh viên thường nộp đơn, được xét ra quyết định và nhận bằng chính thức vào những tháng nào? | `totnghiep::chunk_4`; các mốc thời gian trong quy trình xét tốt nghiệp. | 0.836787 | Có | Sinh viên nộp đơn khoảng tháng 4, được xét tốt nghiệp và ra quyết định vào tháng 8, sau đó nhận bằng và bảng điểm chính thức vào tháng 9. |

**Bao nhiêu câu hỏi trả về chunk có liên quan trong top-3?** **5** / 5

**Điều hay nhất tôi học được từ thành viên khác / nhóm khác (qua demo):**
> Qua quá trình thử nghiệm và so sánh kết quả trong nhóm, tôi nhận thấy chiến lược chia nhỏ văn bản (chunking) kết hợp với lọc siêu dữ liệu (metadata filtering) đóng vai trò quyết định đến độ chính xác của retrieval. Cụ thể, việc gắn các trường thông tin như `audience` (ví dụ `audience=student`) và `category`/`department` giúp loại bỏ hoàn toàn nhiễu từ các văn bản không thuộc đối tượng quan tâm (như quyền mượn của giảng viên/nghiên cứu sinh), từ đó giúp Agent đưa ra câu trả lời chuẩn xác và đầy đủ dữ kiện hơn.

---

## Tự Đánh Giá (Phần Cá Nhân)

| Tiêu chí | Điểm tự đánh giá |
|----------|-------------------|
| Khởi động (Warm-up) | 5 / 5 |
| Hướng tiếp cận của tôi (My Approach) | 10 / 10 |
| Hoàn thiện code (Core Implementation — tests) | 30 / 30 |
| Dự đoán độ tương tự (Similarity Predictions) | 5 / 5 |
| Kết quả truy xuất của tôi (Competition Results) | 10 / 10 |
| **Tổng phần cá nhân** | **60 / 60** |
