from src import LocalEmbedder, compute_similarity


pairs = [
    (
        "Sinh viên phải đóng học phí trước ngày 15 tháng 8.",
        "Hạn cuối thanh toán học phí là ngày 15 tháng 8.",
    ),
    (
        "Sinh viên đăng ký môn học trực tuyến.",
        "Người học có thể đăng ký học phần trên hệ thống.",
    ),
    (
        "Thư viện mở cửa từ thứ hai đến thứ sáu.",
        "Hôm nay trời có mưa lớn.",
    ),
    (
        "Học bổng dành cho sinh viên có thành tích tốt.",
        "Sinh viên xuất sắc có thể được nhận học bổng.",
    ),
    (
        "Ký túc xá không cho phép nấu ăn trong phòng.",
        "Sinh viên phải nộp học phí đúng hạn.",
    ),
]

embedder = LocalEmbedder()

for index, (sentence_a, sentence_b) in enumerate(
    pairs,
    start=1,
):
    vector_a = embedder(sentence_a)
    vector_b = embedder(sentence_b)

    score = compute_similarity(vector_a, vector_b)

    print(f"Cặp {index}: {score:.4f}")