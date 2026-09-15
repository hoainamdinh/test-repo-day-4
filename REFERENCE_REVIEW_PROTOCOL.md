# Private reference review protocol

Hai lane có hai reference khác nhau:

- **Lane S** — reference là **protected gold release** (`$GOLD_RELEASE_DIR`) của baseline kỹ
  thuật. Pilot **không** tạo reference thay thế và **không** sao gold, `$PROTECTED_SOURCE_DIR`
  hay bất kỳ mapping nguồn nào vào repo pilot hoặc repo learner — kể cả trong lịch sử commit.
  Gate G-05 kiểm tự động điều này (`scripts/check-starter-alignment.py`). Gold chỉ được đọc tại
  chỗ trong checkout baseline, và chỉ sau khi nhãn đã khoá (mốc phút 150; thủ tục ở
  `PILOT_TEST_RUNBOOK.md` mục T-06). Hai ký hiệu đường dẫn định nghĩa ở `STARTER_ALIGNMENT.md` mục 1.
- **Lane C** — reference do pilot tự dựng theo thủ tục dưới đây, cho 10 ảnh cabin.

Nhãn Lane C không phải gold của Lane S và ngược lại: luật `v=0` của hai lane mâu thuẫn nhau (D-01).

## Lane C

Reference được giữ tại sibling private path `../day4-private-release/day4-teaching-reference/` hoặc hệ thống riêng có access control. Không commit reference, consent record, raw personal image hoặc reconciled answer key vào student repo.

1. Reviewer A và B tạo task độc lập từ cùng manifest/schema, không xem model hoặc bài nhau.
2. Mỗi người ghi visibility reason cho mọi `v=0/1`, left/right ambiguity và joint khó.
3. So sánh theo image/keypoint: state mismatch và normalized distance; không dùng agreement đơn thuần làm gold.
4. Reconcile dựa trên guideline và evidence ảnh, ghi decision log riêng tư.
5. Reviewer thứ hai xác nhận bản reconcile.
6. Hash export/reference và khóa quyền truy cập.

Student/peer chỉ nhận lỗi mẫu hoặc aggregate insight không làm lộ answer key. Reference chỉ được mở sau submission trong phần debrief đã định trước.
