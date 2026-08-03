# Báo Cáo Nhóm — Lab 7: Embedding & Vector Store

**Nhóm:** DMX
**Thành viên:**

1. Nguyễn Hoàng Biên - 2A202601233
2. Vũ Nguyễn Quốc Đạt - 2A202601199
3. Nguyễn Ngọc Nam - 2A202601561
4. Trần Thị Ngọc Lan - 2A202601385
5. Vũ Tú Quỳnh - 2A202601239
   **Ngày:** 03/08/2026

> **Nộp 1 bản / nhóm.** Phần cá nhân (hướng tiếp cận, kết quả riêng, dự đoán…) mỗi thành viên nộp riêng trong `REPORT_CANHAN.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần nhóm: 40** = Lựa chọn tài liệu (10) + Thiết kế chiến lược (15) + Chất lượng truy xuất (10) + Thuyết trình (5).

---

## 1. Lựa chọn tài liệu (Document Set Quality) — Nhóm (10 điểm)

### Phạm vi bộ tài liệu (Scope)

**Chủ đề (cố định theo lớp K3):** Dịch vụ / quy định đại học (đăng ký môn, học phí, học bổng, thư viện, ký túc xá…).

**Phạm vi cụ thể nhóm tập trung:**

> Nhóm tập trung vào các quy định và dịch vụ sinh viên cốt lõi: Thư viện, Đăng ký học phần, Ký túc xá, Học phí - Học bổng, và Tốt nghiệp.

### Danh sách tài liệu (Data Inventory)

| #   | Tên tài liệu                | Nguồn (Source URL)                                | Ngày lấy / Phiên bản | Số ký tự | Metadata đã gán                                              |
| --- | --------------------------- | ------------------------------------------------- | -------------------- | -------- | ------------------------------------------------------------ |
| 1   | Quy định Tốt nghiệp         | registrar.vinuni.edu.vn/.../tot-nghiep            | 2026-08-03 / 2026.1  | 5,132    | `doc_id`, `source_url`, `version`, `department="Registrar"`  |
| 2   | Tuyển sinh Đại học          | admissions.vinuni.edu.vn/.../tuyen-sinh           | 2026-08-03 / 2026.1  | 8,453    | `doc_id`, `source_url`, `version`, `department="Admissions"` |
| 3   | Chương trình đào tạo        | admissions.vinuni.edu.vn/.../chuong-trinh-dao-tao | 2026-08-03 / 2026.1  | 3,637    | `doc_id`, `source_url`, `version`, `department="Academics"`  |
| 4   | Quy định sử dụng Thư viện   | policy.vinuni.edu.vn/.../library-policies         | 2026-08-03 / 2026.1  | 8,748    | `doc_id`, `source_url`, `version`, `department="Library"`    |
| 5   | Thời khóa biểu & Đăng ký HP | registrar.vinuni.edu.vn/.../thoi-khoa-bieu...     | 2026-08-03 / 2026.1  | 5,681    | `doc_id`, `source_url`, `version`, `department="Registrar"`  |
| 6   | Học phí & Hỗ trợ Tài chính  | admissions.vinuni.edu.vn/.../hoc-phi...           | 2026-08-03 / 2026.1  | 8,129    | `doc_id`, `source_url`, `version`, `department="Admissions"` |
| 7   | Cuộc sống tại Ký túc xá     | admissions.vinuni.edu.vn/.../cau-hoi...           | 2026-08-03 / 2026.1  | 4,956    | `doc_id`, `source_url`, `version`, `department="Admissions"` |

**Danh sách kiểm tra quản trị dữ liệu (Data governance checklist):**

- [x] Tập tài liệu (Corpus) chỉ chứa nguồn công khai/được phép dùng và không chứa dữ liệu cá nhân, thông tin đăng nhập hoặc tài liệu nội bộ.
- [x] Mỗi tài liệu có `source_url`, `retrieved_at`, `document_version` (hoặc ngày hiệu lực) trong metadata.
- [x] Tập tài liệu (Corpus) chỉ chứa nguồn công khai/được phép dùng và không chứa dữ liệu cá nhân, thông tin đăng nhập hoặc tài liệu nội bộ.
- [x] Mỗi tài liệu có `source_url`, `retrieved_at`, `document_version` (hoặc ngày hiệu lực) trong metadata.

### Cấu trúc Metadata (Metadata Schema)

| Trường metadata      | Kiểu   | Ví dụ giá trị              | Tại sao hữu ích cho truy xuất (retrieval)?                                                    |
| -------------------- | ------ | -------------------------- | --------------------------------------------------------------------------------------------- |
| `doc_id`             | String | `thuvien`, `ktx`           | Định danh duy nhất để tránh trùng lặp, hữu ích khi cần xóa/cập nhật tài liệu.                 |
| Trường metadata      | Kiểu   | Ví dụ giá trị              | Tại sao hữu ích cho truy xuất (retrieval)?                                                    |
| -------------------- | ------ | -------------------------- | --------------------------------------------------------------------------------------------- |
| `doc_id`             | String | `thuvien`, `ktx`           | Định danh duy nhất để tránh trùng lặp, hữu ích khi cần xóa/cập nhật tài liệu.                 |
| `department`         | String | `Library`, `Registrar`     | Dùng để filter theo phòng ban, giúp mô hình tập trung vào context chính xác nhất.             |
| `document_version`   | String | `2026.1`                   | Lọc ra văn bản quy định mới nhất, tránh trả lời thông tin cũ đã hết hạn.                      |
| `document_version`   | String | `2026.1`                   | Lọc ra văn bản quy định mới nhất, tránh trả lời thông tin cũ đã hết hạn.                      |

---

## 2. Thiết kế chiến lược (Strategy Design) — Nhóm (15 điểm)

> Mỗi thành viên thử **một chiến lược khác nhau** trên cùng bộ tài liệu; nhóm tổng hợp và so sánh ở đây.

### Phân tích đường cơ sở (Baseline Analysis)

Chạy `ChunkingStrategyComparator().compare()` trên 2-3 tài liệu:

| Tài liệu                       | Chiến lược (Strategy)            | Số lượng Chunk | Độ dài trung bình | Giữ được ngữ cảnh không?                                                                                                                            |
| ------------------------------ | -------------------------------- | -------------- | ----------------- | --------------------------------------------------------------------------------------------------------------------------------------------------- |
| Toàn bộ corpus K3 (9 tài liệu) | FixedSizeChunker (`fixed_size`)  | 194            | 196.4             | Một phần; kích thước ổn định nhưng có thể cắt giữa câu hoặc giữa câu hỏi và câu trả lời.                                                            |
| Toàn bộ corpus K3 (9 tài liệu) | ChunkByHeader (`by_header`)      | 53             | 717.2             | Tốt hơn; giữ heading và nội dung theo từng mục, nhưng một số section quá dài.                                                                       |
| Corpus`data_nhom` (7 tài liệu) | SentenceChunker (`by_sentences`) | 99             | 348,18            | Tốt; giữ ranh giới câu và nhóm câu hỏi-trả lời, nhưng một số mục Markdown dài làm chunk vượt kích thước mong muốn.                                  |
| Toàn bộ corpus K3 (9 tài liệu) | RecursiveChunker (`recursive`)   | 239            | 157.41            | Có — giữ được ngữ cảnh tốt hơn, ưu tiên tách theo đoạn văn, heading và dòng ngắt, nhưng số lượng chunk có thể nhiều hơn so với các chiến lược khác. |

### Chiến lược của từng thành viên

> Mỗi thành viên điền một khối dưới đây (copy thêm nếu nhóm có nhiều hơn 3 người).

**Thành viên 1 — Vũ Tú Quỳnh**

- **Loại chiến lược:** Fixed Size và Chunk By Header
- **Mô tả & lý do chọn cho chủ đề này:**
  - **Fixed Size:** Chia văn bản thành các chunk có kích thước cố định 200 ký tự, không overlap. Chiến lược này dễ triển khai, tạo các chunk đồng đều và phù hợp để kiểm soát kích thước đầu vào cho embedding. Tuy nhiên, ranh giới cắt có thể nằm giữa câu hỏi, câu trả lời hoặc một ý đang diễn đạt.
  - **Chunk By Header:** Chia tài liệu Markdown tại các heading từ `#` đến `######` và giữ heading ở đầu mỗi chunk. Cách này phù hợp với bộ dữ liệu quy định đại học vì tài liệu có cấu trúc theo các mục như học phí, học bổng, đăng ký môn học và thư viện; nhờ vậy chunk giữ được ngữ cảnh và dễ truy vết chủ đề hơn.
- **Kết quả chạy thử trên corpus:** Với 9 tài liệu trong `data/k3_university`, Fixed Size tạo 194 chunk, độ dài trung bình 196.4 ký tự/chunk. Chunk By Header tạo 53 chunk, độ dài trung bình 717.2 ký tự/chunk; chunk dài nhất vượt 6,000 ký tự ở tài liệu có ít heading.
- **Nhận xét:** Fixed Size có kích thước ổn định và thuận lợi cho embedding nhưng có thể làm mất ngữ cảnh do cắt giữa ý. Chunk By Header bảo toàn cấu trúc tốt hơn nhưng kích thước không đồng đều, một số section quá dài có thể làm loãng kết quả tìm kiếm. Phương án phù hợp nhất là tách theo header trước, sau đó tiếp tục chia các section quá dài bằng Fixed Size hoặc Recursive Chunking.
- **Code snippet (nếu custom):**

```python
from src.chunking import FixedSizeChunker, HeaderChunker

fixed_chunks = FixedSizeChunker(chunk_size=200, overlap=0).chunk(text)
header_chunks = HeaderChunker().chunk(text)
```

**Thành viên 2 — Trần Thị Ngọc Lan**

- **Loại chiến lược: Recursive**
- **Mô tả & lý do chọn: Chiến lược này ưu tiên tách tài liệu tại các ranh giới tự nhiên như đoạn văn, tiêu đề Markdown và các dòng ngắt trước khi chuyển sang các dấu phân cách nhỏ hơn. Điều này giúp giữ được ngữ cảnh của từng phần nội dung, tránh cắt ngang giữa các ý tưởng liên quan và tạo ra các chunk mạch lạc hơn cho quá trình retrieval. Vì tài liệu trong K3_university có cấu trúc rõ ràng theo mục, tiêu đề và nội dung, nên RecursiveChunker phù hợp để bảo toàn ý nghĩa của từng phần.\*\***
- **Code snippet (nếu custom):**

```python
from Ngoc_Lan_01385.chunking import RecursiveChunker

chunker = RecursiveChunker(chunk_size=500)
chunks = chunker.chunk(text)
```

**Thành viên 3 — Nguyễn Ngọc Nam**

- **Loại chiến lược:** Sentence Chunking với `SentenceChunker(max_sentences_per_chunk=3)`.
- **Mô tả & lý do chọn:** Tách văn bản theo ranh giới câu bằng regex và gom tối đa 3 câu vào một chunk. Chiến lược phù hợp với tài liệu FAQ, hướng dẫn và quy định vì giữ được câu hỏi-trả lời tương đối trọn vẹn, dễ đọc và dễ kiểm tra thủ công.
- **Embedding và retrieval:** Dùng Gemini Embedding 2 (`gemini-embedding-2`, vector 768 chiều), nạp 7 tài liệu thành 99 chunks, tìm Top-3 bằng `EmbeddingStore` và đưa context vào `KnowledgeBaseAgent`.
- **Kết quả trên 5 benchmark query:** 5/5 câu có chunk liên quan trong Top-3; 5/5 câu có chunk đúng chủ đề ở Top-1. Điểm Top-1 lần lượt là 0,777044; 0,789366; 0,735846; 0,831314; 0,836787.
- **Hạn chế:** Dữ liệu hiện tại chưa có YAML front matter `audience`, nên chưa thể kiểm tra đầy đủ câu hỏi lọc metadata. `demo_llm` chỉ kiểm tra việc truyền context, chưa phải LLM sinh câu trả lời thật.
- **Code snippet:**

```python
from src import GeminiEmbedder, SentenceChunker
from ingest import build_knowledge_base

chunker = SentenceChunker(max_sentences_per_chunk=3)
embedder = GeminiEmbedder()
store = build_knowledge_base(
    "data_nhom",
    embedding_fn=embedder,
    chunker=chunker,
    collection_name="person4_sentence_group_final",
)
```

### So Sánh Giữa Các Thành Viên

| Thành viên  | Chiến lược (Strategy)         | Điểm truy xuất (/10) | Điểm mạnh                                                                         | Điểm yếu                                                                 |
| ----------- | ----------------------------- | -------------------- | --------------------------------------------------------------------------------- | ------------------------------------------------------------------------ |
| Người 4     | Sentence + Gemini Embedding 2 | 5/5 Top-3; 5/5 Top-1 | Chunk mạch lạc, retrieval đúng chủ đề                                             | Một số chunk dài; chưa có metadata`audience`; agent đang dùng `demo_llm` |
| Vũ Tú Quỳnh | Fixed Size                    | 7/10                 | Kích thước chunk ổn định, dễ embedding, tốc độ xử lý và lưu trữ dễ dự đoán        | Có thể cắt giữa câu hoặc giữa câu hỏi và câu trả lời, làm mất ngữ cảnh   |
| Vũ Tú Quỳnh | Chunk by header               | 8/10                 | Giữ được heading và nội dung theo từng mục, chunk có tính mạch lạc và dễ truy vết | Kích thước chunk không đồng đều, một số section quá dài                  |

### So sánh công bằng giữa các chiến lược

| Chiến lược             | Context@3 | Agent facts | Agent trả lời đủ | Điểm rubric (/10) | Điểm mạnh                                                      | Điểm yếu                                                         |
| ---------------------- | --------: | ----------: | ---------------: | ----------------: | -------------------------------------------------------------- | ---------------------------------------------------------------- |
| Fixed Size 500/50      |   **88%** |     **75%** |              40% |             **7** | Cao nhất về context và dữ kiện Agent; Q1, Q5 đạt 2/2           | Q2–Q4 còn thiếu dữ kiện                                          |
| Sentence 3             |       73% |         70% |              40% |                 6 | Q1, Q5 đầy đủ; Q4 đạt 80% dữ kiện                              | Q3 không truy xuất được chunk liên quan                          |
| Recursive 500          |       78% |         73% |              40% |             **7** | Cân bằng giữa context và câu trả lời; Q2 đạt 86% dữ kiện Agent | Q3 Agent không lấy được dữ kiện dù context có một phần liên quan |
| Header                 |       73% |         70% |              40% |                 6 | Ít chunk nhất; Q1, Q5 đầy đủ                                   | Q3 thất bại; section dài tới 6,246 ký tự                         |
| Header + Recursive 500 |       73% |         73% |              40% |                 6 | Q2 đạt 86% dữ kiện Agent; kích thước chunk được kiểm soát      | Q3 thất bại; tạo nhiều chunk nhất                                |

**Chiến lược tốt nhất:** `FixedSizeChunker(chunk_size=500, overlap=50)` đạt **7/10**, `context@3=88%` và `agent_facts=75%`. Recursive 500 cũng đạt 7/10 nhưng đứng sau do `context@3=78%` và `agent_facts=73%`.

Thời gian tìm kiếm BM25 chỉ khoảng 10–14 ms cho 5 query mỗi chiến lược. Thời gian gọi LLM khoảng 18–21 giây/chiến lược khi đã tính thời gian giãn cách theo quota; toàn bộ lần chạy hoàn tất trong khoảng 107 giây.

---

## 3. Câu hỏi đánh giá & Chất lượng truy xuất (Retrieval Quality) — Nhóm (10 điểm)

### Câu hỏi đánh giá & Câu trả lời chuẩn (nhóm thống nhất)

> **Đúng 5 câu hỏi**, đa dạng, có thể kiểm chứng; **ít nhất 1 câu** cần lọc metadata mới trả lời tốt. Đây là bộ câu hỏi chung cho mọi thành viên chạy.

| #   | Câu hỏi (Query)                                                                                                                                                                                                           | Câu trả lời chuẩn (Gold Answer)                                                                                                                                                                                                                      | Chunk nào chứa thông tin?                           |
| --- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------- |
| 1   | Trên hệ thống SIS, trạng thái nào xác nhận sinh viên đã đăng ký môn học thành công, trạng thái “Selected” có ý nghĩa gì và sinh viên kiểm tra lại danh sách môn đã đăng ký ở đâu?                                         | Môn học phải có trạng thái**“Registered”**. “Selected” nghĩa là mới chọn nhưng chưa đăng ký thành công. Danh sách môn được kiểm tra tại**“Your Class Schedule”**.                                                                                    | `dangkymonhoc.md` (Cách sử dụng SIS)                |
| 2   | Sinh viên năm nhất có bắt buộc ở ký túc xá không? Quy định thay đổi thế nào từ năm hai và trường hợp sức khỏe hoặc tôn giáo được xử lý ra sao?                                                                            | Sinh viên năm nhất**bắt buộc** ở ký túc xá; từ năm hai trở đi thì không còn bắt buộc. Trường hợp bất khả kháng về sức khỏe hoặc tôn giáo có thể làm đơn đề nghị đặc cách để Nhà trường xem xét.                                                      | `ktx.md` (Ở ký túc xá có bắt buộc không?)           |
| 3   | Theo quyền mượn tài liệu thư viện dành cho sinh viên đại học, một sinh viên được mượn tối đa bao nhiêu tài liệu, trong bao lâu và được gia hạn mấy lần?                                                                   | Sinh viên đại học được mượn tối đa**3 tài liệu**, trong **2 tuần** và được **gia hạn 1 lần**. _(Lưu ý: Dùng `metadata_filter={"audience": "student"}`)_                                                                                              | `thuvien.md` (2.2. Circulation Privileges)          |
| 4   | VinUni cho phép nộp học phí bằng những hình thức nào và thu học phí vào những thời điểm nào trong năm?                                                                                                                    | Có hai hình thức: quẹt thẻ Visa trực tiếp tại Phòng Kế toán – Tài chính hoặc chuyển tiền online qua Salesforce. Học phí được đóng thành**2 đợt/năm**, vào đầu kỳ Mùa thu và kỳ Mùa Xuân.                                                             | `hocphi_hocbong.md` (Học phí)                       |
| 5   | Theo quy trình xét tốt nghiệp, sinh viên thường nộp đơn, được xét ra quyết định và nhận bằng chính thức vào những tháng nào?                                                                                              | Sinh viên nộp đơn khoảng**tháng 4**, được xét tốt nghiệp và ra quyết định vào **tháng 8**, sau đó nhận bằng và bảng điểm vào **tháng 9**.                                                                                                            | `totnghiep.md` (Quy trình xét tốt nghiệp)           |
| #   | Câu hỏi (Query)                                                                                                                                                                                                           | Câu trả lời chuẩn (Gold Answer)                                                                                                                                                                                                                      | Chunk nào chứa thông tin?                           |
| -   | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------- |
| 1   | Trên hệ thống SIS, trạng thái nào xác nhận sinh viên đã đăng ký môn học thành công, trạng thái “Selected” có ý nghĩa gì và sinh viên kiểm tra lại danh sách môn đã đăng ký ở đâu?                                         | Môn học phải có trạng thái**“Registered”**. “Selected” nghĩa là mới chọn nhưng chưa đăng ký thành công. Danh sách môn được kiểm tra tại**“Your Class Schedule”**.                                                                                    | `dangkymonhoc.md` (Cách sử dụng SIS)                |
| 2   | Sinh viên năm nhất có bắt buộc ở ký túc xá không? Quy định thay đổi thế nào từ năm hai và trường hợp sức khỏe hoặc tôn giáo được xử lý ra sao?                                                                            | Sinh viên năm nhất**bắt buộc** ở ký túc xá; từ năm hai trở đi thì không còn bắt buộc. Trường hợp bất khả kháng về sức khỏe hoặc tôn giáo có thể làm đơn đề nghị đặc cách để Nhà trường xem xét.                                                      | `ktx.md` (Ở ký túc xá có bắt buộc không?)           |
| 3   | Theo quyền mượn tài liệu thư viện dành cho sinh viên đại học, một sinh viên được mượn tối đa bao nhiêu tài liệu, trong bao lâu và được gia hạn mấy lần?                                                                   | Sinh viên đại học được mượn tối đa**3 tài liệu**, trong **2 tuần** và được **gia hạn 1 lần**. _(Lưu ý: Dùng `metadata_filter={"audience": "student"}`)_                                                                                              | `thuvien.md` (2.2. Circulation Privileges)          |
| 4   | VinUni cho phép nộp học phí bằng những hình thức nào và thu học phí vào những thời điểm nào trong năm?                                                                                                                    | Có hai hình thức: quẹt thẻ Visa trực tiếp tại Phòng Kế toán – Tài chính hoặc chuyển tiền online qua Salesforce. Học phí được đóng thành**2 đợt/năm**, vào đầu kỳ Mùa thu và kỳ Mùa Xuân.                                                             | `hocphi_hocbong.md` (Học phí)                       |
| 5   | Theo quy trình xét tốt nghiệp, sinh viên thường nộp đơn, được xét ra quyết định và nhận bằng chính thức vào những tháng nào?                                                                                              | Sinh viên nộp đơn khoảng**tháng 4**, được xét tốt nghiệp và ra quyết định vào **tháng 8**, sau đó nhận bằng và bảng điểm vào **tháng 9**.                                                                                                            | `totnghiep.md` (Quy trình xét tốt nghiệp)           |

### Tổng hợp chất lượng truy xuất của nhóm

> Cách chấm (theo `docs/SCORING.md`): **2 điểm/câu** — top-3 chứa chunk liên quan + agent trả lời đúng (2), có liên quan nhưng thiếu/không ở top-1 (1), không có trong top-3 (0).

| #   | Câu hỏi           | Chiến lược tốt nhất cho câu này | Có chunk liên quan trong top-3?                                                                                        | Ghi chú |
| --- | ----------------- | ------------------------------- | ---------------------------------------------------------------------------------------------------------------------- | ------- |
| 1   | Sentence + Gemini | Có                              | Top-1`dangkymonhoc::chunk_9`, score 0,777044; Top-3 chứa trạng thái `Registered`, `Selected` và `Your Class Schedule`. |         |
| 2   | Sentence + Gemini | Có                              | Top-1`ktx::chunk_1`, score 0,789366; Top-3 giữ nội dung bắt buộc năm nhất và ngoại lệ sức khỏe/tôn giáo.               |         |
| 3   | Sentence + Gemini | Có                              | Top-1`thuvien::chunk_13`, score 0,735846; chứa bảng quyền mượn tài liệu của sinh viên đại học.                         |         |
| 4   | Sentence + Gemini | Có                              | Top-1`hocphi_hocbong::chunk_2`, score 0,831314; chứa hình thức thanh toán và 2 đợt đóng học phí/năm.                   |         |
| 5   | Sentence + Gemini | Có                              | Top-1`totnghiep::chunk_4`, score 0,836787; chứa tháng xét tốt nghiệp và phát hành bằng chính thức.                     |         |

> **Lưu ý về Agent:** `KnowledgeBaseAgent.answer()` đã được chạy cho cả 5 câu và nhận đúng context retrieval, nhưng `demo_llm` hiện chỉ trả preview của prompt. Vì vậy các kết quả trên xác nhận chất lượng retrieval; chưa nên quy đổi thành điểm Agent Answer hoàn chỉnh cho đến khi nhóm dùng LLM sinh câu trả lời thật.
> Chấm theo `docs/SCORING.md`: 2 điểm khi Top-3 có chunk liên quan và Agent Answer chính xác; 1 điểm khi Top-3 có chunk liên quan nhưng câu trả lời thiếu chi tiết hoặc chunk liên quan không ở Top-1; 0 điểm khi Top-3 không có chunk liên quan.

Agent dùng `gemini-3.1-flash-lite`, `temperature=0` và chỉ được phép trả lời từ Top-3 context. Câu trả lời được đối chiếu tự động với các nhóm dữ kiện bắt buộc trong gold answer.

|   # | Chiến lược tốt nhất             | Context Top-3 | Dữ kiện trong Agent Answer | Điểm | Đánh giá theo rubric                                                                                                                  |
| --: | ------------------------------- | ------------: | -------------------------: | ---: | ------------------------------------------------------------------------------------------------------------------------------------- |
|   1 | Tất cả chiến lược               |          100% |                       100% |  2/2 | Top-1 liên quan; Agent trả lời đủ`Registered`, `Selected` và `Your Class Schedule`.                                                   |
|   2 | Recursive hoặc Header+Recursive |           86% |                    **86%** |  1/2 | Có chunk liên quan nhưng Agent còn thiếu một dữ kiện về quy định KTX.                                                                 |
|   3 | Fixed Size 500/50               |       **75%** |                    **25%** |  1/2 | Top-3 có chunk liên quan nhưng Agent chỉ nêu được một phần quyền mượn; các chiến lược Sentence/Header không tìm được chunk liên quan. |
|   4 | Tất cả chiến lược               |           80% |                        80% |  1/2 | Agent nêu được phần lớn thông tin học phí nhưng chưa đủ toàn bộ hình thức và thời điểm.                                               |
|   5 | Tất cả chiến lược               |          100% |                       100% |  2/2 | Top-1 liên quan; Agent trả lời đủ tháng 4, tháng 8 và tháng 9.                                                                        |

**Tổng điểm Chất lượng Truy xuất: 7/10.**

Điểm này không còn là proxy context: cả retrieval và câu trả lời Agent đã được chạy thực tế. Q1 và Q5 đạt trọn 2 điểm; Q2–Q4 đạt 1 điểm do context hoặc câu trả lời còn thiếu dữ kiện.

**Lọc bằng metadata có giúp ích không?**

Có. Các bộ lọc `department`, `category` và `audience` loại trung bình **83–86%** số chunk trước khi BM25 xếp hạng, nhờ đó truy vấn chỉ cạnh tranh trong đúng nhóm tài liệu. Câu 3 dùng `department=library`, `category=library-policies`, `audience=student` để loại tài liệu thư viện mẫu và các tài liệu ngoài chính sách mượn. Tuy nhiên, metadata chỉ thu hẹp phạm vi; nó không giải quyết được việc query tiếng Việt nhưng bảng dữ kiện viết bằng tiếng Anh, nên Q3 vẫn là failure case chính.

---

## 4. Thuyết trình (Demo) & Bài học nhóm — Nhóm (5 điểm)

**Những phân tích (insights) hay nhất nhóm sẽ trình bày:**

- Fixed Size 500/50 đứng đầu với 7/10, `context@3=88%` và `agent_facts=75%`; Recursive cùng 7/10 nhưng độ phủ thấp hơn nhẹ.
- Agent trả lời đầy đủ Q1 và Q5 ở mọi chiến lược. Q2 và Q4 chỉ thiếu một phần dữ kiện, cho thấy chất lượng Agent bị giới hạn trực tiếp bởi context truy xuất.
- Metadata filtering giảm 83–86% không gian tìm kiếm mà không cần embedding; tuy nhiên nó không xử lý được chênh lệch ngôn ngữ giữa query tiếng Việt và bảng dữ liệu tiếng Anh.

**Bài học rút ra khi so sánh trong nhóm:**

Overlap giúp Fixed Size giữ dữ kiện qua ranh giới và tạo context tốt nhất cho Agent. Recursive cho kết quả gần tương đương và tốt hơn ở Q2, trong khi Header thuần có section quá dài còn Sentence/Header+Recursive làm mất khả năng tìm đúng bảng ở Q3.

**Failure case:**

Q3 là lỗi rõ nhất. Fixed Size lấy được 75% dữ kiện trong context nhưng Agent chỉ trả lại 25%; Recursive có 25% context nhưng Agent không trả lại dữ kiện chuẩn; Sentence, Header và Header+Recursive đều không tìm được chunk liên quan. Nguyên nhân chính là câu hỏi tiếng Việt trong khi bảng nguồn dùng các cụm tiếng Anh như `Undergraduate Students`, `2 weeks`, `1 time`.

**Nếu làm lại, nhóm sẽ thay đổi gì trong chiến lược dữ liệu (data strategy)?**

## Nhóm sẽ chuẩn hóa bảng thư viện thành câu tiếng Việt, bổ sung metadata song ngữ (`topic`, `user_group`, `content_language`) và lặp lại heading trong mỗi chunk con. Sau đó nhóm sẽ chạy lại cùng benchmark với nhiều lần sinh để kiểm tra độ ổn định của Agent, thay vì kết luận từ một lần gọi LLM duy nhất.

## Tự Đánh Giá (Phần Nhóm)

| Tiêu chí                                     | Điểm tự đánh giá       |
| -------------------------------------------- | ---------------------- |
| Lựa chọn tài liệu (Document Set Quality)     | / 10                   |
| Thiết kế chiến lược (Strategy Design)        | / 15                   |
| Chất lượng truy xuất (Retrieval Quality)     | / 10                   |
| Thuyết trình (Demo)                          | / 5                    |
| **Tổng phần nhóm**                           | **/ 40**               |
| Tiêu chí                                     | Điểm tự đánh giá       |
| -------------------------------------------- | ---------------------- |
| Lựa chọn tài liệu (Document Set Quality)     | 9/ 10                  |
| Thiết kế chiến lược (Strategy Design)        | 13/ 15                 |
| Chất lượng truy xuất (Retrieval Quality)     | 7 / 10                 |
| Thuyết trình (Demo)                          | 5/ 5                   |
| **Tổng phần nhóm**                           | **34 / 40**            |
