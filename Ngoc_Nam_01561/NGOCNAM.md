# Báo Cáo Cá Nhân — Lab 7: Embedding & Vector Store

**Họ tên:** Nguyễn Ngọc Nam
**Nhóm:** 2A
**Ngày:** 03/08/2026

**Tổng điểm phần cá nhân: 60** = Khởi động (5) + Hướng tiếp cận (10) + Hoàn thiện code (30) + Dự đoán độ tương tự (5) + Kết quả truy xuất (10).

---

## 1. Khởi động (Warm-up) — Cá nhân (5 điểm)

### Độ tương tự Cosine (Cosine Similarity) (Bài tập 1.1)

Độ tương tự cosine cao nghĩa là hai vector embedding có hướng gần nhau, tức là hai đoạn văn bản có nội dung hoặc ý nghĩa gần nhau trong không gian embedding. Giá trị thấp hoặc âm cho thấy hai vector ít tương đồng hoặc có hướng đối lập.

**Ví dụ có độ tương tự CAO:**

- Câu A: Sinh viên đăng ký học phần trong cổng học vụ.
- Câu B: Sinh viên thực hiện đăng ký môn học trên cổng học vụ.
- Tại sao tương đồng: Hai câu cùng nói về sinh viên đăng ký môn học qua cổng học vụ.

**Ví dụ có độ tương tự THẤP:**

- Câu A: Sinh viên cần kiểm tra học phần tiên quyết.
- Câu B: Thư viện cung cấp không gian học tập.
- Tại sao khác: Một câu nói về điều kiện đăng ký môn học, câu còn lại nói về dịch vụ thư viện.

Cosine similarity thường phù hợp với text embedding hơn Euclidean distance vì nó tập trung vào hướng của vector, ít bị ảnh hưởng bởi độ lớn tuyệt đối của vector. Điều này phù hợp với việc so sánh ý nghĩa văn bản, đặc biệt khi embedding đã được chuẩn hóa.

### Bài toán tính toán Chunking (Bài tập 1.2)

Với tài liệu dài 10.000 ký tự, `chunk_size=500`, `overlap=50`:

```text
step = 500 - 50 = 450
số chunk = ceil((10.000 - 50) / 450)
          = ceil(9.950 / 450)
          = 23 chunk
```

Nếu `overlap=100`:

```text
step = 500 - 100 = 400
số chunk = ceil((10.000 - 100) / 400)
          = ceil(9.900 / 400)
          = 25 chunk
```

Overlap lớn hơn làm tăng số chunk vì mỗi bước di chuyển ngắn hơn. Đổi lại, thông tin ở ranh giới giữa hai chunk được lặp lại, giúp giảm nguy cơ mất ngữ cảnh khi một câu hoặc một quy định bị cắt giữa hai chunk.

---

## 2. Hướng tiếp cận của tôi (My Approach) — Cá nhân (10 điểm)

### Các hàm chia nhỏ (Chunking Functions)

**`SentenceChunker.chunk`** — hướng tiếp cận:

Hàm dùng biểu thức chính quy `(?<=[.!?])\s+` để tách sau các dấu kết thúc câu nhưng vẫn giữ lại dấu câu. Các câu rỗng được loại bỏ, sau đó được gom thành từng nhóm có tối đa `max_sentences_per_chunk` câu. Trường hợp văn bản rỗng trả về danh sách rỗng.

**`RecursiveChunker.chunk` / `_split`** — hướng tiếp cận:

Thuật toán thử các separator theo thứ tự ưu tiên: đoạn văn, xuống dòng, dấu chấm và khoảng trắng. Nếu đoạn sau khi tách vẫn lớn hơn `chunk_size`, hàm đệ quy gọi lại với separator có độ ưu tiên thấp hơn. Base case là đoạn đã nhỏ hơn giới hạn; nếu không còn separator thì cắt cứng theo `chunk_size`.

### Lớp EmbeddingStore

**`add_documents` + `search`** — hướng tiếp cận:

Mỗi `Document` được chuẩn hóa thành record gồm `id`, `content`, `metadata` và `embedding`. Với backend mặc định, record được lưu trong bộ nhớ. Khi tìm kiếm, query được embed rồi tính dot product với các embedding đã lưu; kết quả được sắp xếp theo score giảm dần và cắt lấy `top_k`.

**`search_with_filter` + `delete_document`** — hướng tiếp cận:

`search_with_filter` lọc metadata trước, yêu cầu mọi cặp key-value trong filter phải khớp, rồi mới thực hiện similarity search trên các record còn lại. `delete_document` xóa các record có `metadata['doc_id']` tương ứng; đồng thời hỗ trợ xóa record có `id` trùng `doc_id`.

### Tác tử KnowledgeBaseAgent

**`answer`** — hướng tiếp cận:

Agent gọi `store.search()` để lấy các chunk liên quan, ghép chúng thành phần `Ngữ cảnh` trong prompt và thêm câu hỏi của người dùng. Prompt yêu cầu mô hình chỉ trả lời dựa trên context và nói rõ khi tài liệu không đủ thông tin, sau đó gọi `llm_fn` để sinh câu trả lời.

---

## 3. Hoàn thiện code (Core Implementation) — Cá nhân (30 điểm)

Đã hoàn thành các TODO trong:

- `src/chunking.py`: sentence chunking, recursive chunking, cosine similarity và comparator.
- `src/store.py`: lưu embedding, tìm kiếm, lọc metadata, đếm và xóa document.
- `src/agent.py`: retrieval-augmented prompt và gọi LLM.

### Kết Quả Kiểm Thử (Test Results)

Đã chạy:

```powershell
.\.venv\Scripts\python.exe -m pytest tests/ -v
```

Kết quả:

```text
42 passed in 0.11s
```

**Số lượng bài test vượt qua (pass):** 42 / 42

Ngoài ra, `ingest.py` self-check và demo `main.py` đều chạy thành công với mock embedding.

---

## 4. Dự đoán độ tương tự (Similarity Predictions) — Cá nhân (5 điểm)

Các điểm dưới đây được tính bằng `_mock_embed`. Mock embedder tạo vector xác định theo chuỗi nhưng gần như ngẫu nhiên theo nội dung, vì vậy điểm số không đại diện tốt cho similarity ngữ nghĩa tiếng Việt.

| Cặp | Câu A                                                      | Câu B                                                 | Dự đoán | Điểm thực tế | Đúng?                |
| --- | ---------------------------------------------------------- | ----------------------------------------------------- | ------- | ------------ | -------------------- |
| 1   | Sinh viên đăng ký học phần trong cổng học vụ.              | Sinh viên thực hiện đăng ký môn học trên cổng học vụ. | cao     | 0.063129     | Không theo điểm mock |
| 2   | Thư viện cung cấp dịch vụ mượn tài liệu.                   | Người dùng có thể mượn sách tại thư viện.             | cao     | -0.037205    | Không theo điểm mock |
| 3   | Sinh viên cần kiểm tra học phần tiên quyết.                | Thư viện cung cấp không gian học tập.                 | thấp    | -0.081920    | Có                   |
| 4   | Khi gặp lỗi trùng lịch, sinh viên điều chỉnh lớp học phần. | Người dùng cần mang thẻ định danh khi mượn tài liệu.  | thấp    | 0.009960     | Có                   |
| 5   | Python hỗ trợ xây dựng hệ thống RAG.                       | Học phí được thanh toán theo quy định của trường.     | thấp    | -0.093018    | Có                   |

Kết quả bất ngờ nhất là hai cặp có nội dung gần nhau không nhận được điểm cao. Điều này cho thấy mock embedding chỉ thích hợp để kiểm tra tính đúng đắn của pipeline và unit test, không phù hợp để đánh giá chất lượng ngữ nghĩa. Khi benchmark thật, cần dùng local multilingual embedder với `EMBEDDING_PROVIDER=local`.

---

## 5. Kết quả truy xuất của tôi (Competition Results) — Cá nhân (10 điểm)

> Bảng dưới đây chạy trên 2 tài liệu khởi động trong `data/k3_university/`, sử dụng `FixedSizeChunker(chunk_size=500, overlap=50)` và mock embedding. Đây chưa phải kết quả benchmark chính thức của nhóm vì corpus hiện chưa đủ 5–10 tài liệu và nhóm chưa thống nhất 5 câu hỏi cuối cùng.

| #   | Câu hỏi (Query)                                                                      | Top-1 Chunk truy xuất được (tóm tắt)                                                    | Điểm Score | Có liên quan không? (Relevant) | Câu trả lời của Agent (tóm tắt)                                                             |
| --- | ------------------------------------------------------------------------------------ | --------------------------------------------------------------------------------------- | ---------- | ------------------------------ | ------------------------------------------------------------------------------------------- |
| 1   | Sinh viên đăng ký học phần ở đâu và theo lịch nào?                                   | `k3-course-registration::chunk_1`, chứa phần cuối hướng dẫn đăng ký và xử lý trùng lịch | 0.002375   | Một phần                       | Demo LLM nhận context nhưng chưa tạo câu trả lời nghiệp vụ thật                             |
| 2   | Sinh viên cần kiểm tra điều kiện gì trước khi xác nhận đăng ký?                      | `k3-library-services::chunk_0`                                                          | 0.193906   | Không                          | Kết quả bị lệch sang tài liệu thư viện do mock embedding                                    |
| 3   | Xử lý lỗi trùng lịch học phần như thế nào?                                           | `k3-library-services::chunk_0`                                                          | 0.073844   | Không                          | Kết quả chưa grounding đúng vào tài liệu đăng ký học phần                                   |
| 4   | Thư viện cung cấp những dịch vụ nào?                                                 | `k3-course-registration::chunk_1`                                                       | 0.028844   | Không                          | Kết quả bị lệch do mock embedding                                                           |
| 5   | Quy định dành cho sinh viên về đăng ký học phần là gì? _(filter `audience=student`)_ | `k3-course-registration::chunk_1`                                                       | 0.197968   | Một phần                       | Filter loại được tài liệu không dành cho sinh viên; demo LLM vẫn chỉ trả preview của prompt |

**Bao nhiêu câu hỏi trả về chunk có liên quan trong top-3?** 2 / 5 theo đánh giá tạm thời.

Kết quả cho thấy pipeline kỹ thuật đã hoạt động, nhưng mock embedding làm thứ hạng retrieval gần như ngẫu nhiên. Metadata filter `audience=student` có ích vì thu hẹp kết quả về đúng tài liệu đăng ký học phần, tuy nhiên cần corpus thật, local embedding và LLM thật để đánh giá chất lượng cuối cùng.

**Điều hay nhất tôi học được từ thành viên khác / nhóm khác:**

> Cần đánh giá chunking trên cùng một bộ câu hỏi và cùng corpus; không thể kết luận chiến lược tốt chỉ từ số lượng chunk hoặc việc test code đã pass. Metadata và chất lượng nguồn tài liệu có thể ảnh hưởng trực tiếp đến grounding của agent.

---

## Tự Đánh Giá (Phần Cá Nhân)

| Tiêu chí                                        | Điểm tự đánh giá             |
| ----------------------------------------------- | ---------------------------- |
| Khởi động (Warm-up)                             | 5 / 5                        |
| Hướng tiếp cận của tôi (My Approach)            | 10 / 10                      |
| Hoàn thiện code (Core Implementation — tests)   | 30 / 30                      |
| Dự đoán độ tương tự (Similarity Predictions)    | 5 / 5                        |
| Kết quả truy xuất của tôi (Competition Results) | Chờ benchmark nhóm / 10      |
| **Tổng phần cá nhân**                           | **50 + điểm benchmark / 60** |
