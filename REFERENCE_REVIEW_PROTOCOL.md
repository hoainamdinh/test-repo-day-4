# Private reference review protocol

Reference chính thức là **protected gold release** (`$GOLD_RELEASE_DIR` / `gold_labels.zip`) của baseline kỹ thuật.


- Pilot **không** sao chép gold hay bất kỳ mapping nguồn nào vào repo người học trước khi nhãn đã khoá.
- Gate G-05 kiểm tự động điều này (`scripts/check-starter-alignment.py`). Gold set (`gold_labels.zip`) chỉ được cung cấp cho học viên/Colab sau khi cả lớp đã hoàn thành và khoá nhãn (mốc phút 150; thủ tục ở `PILOT_TEST_RUNBOOK.md`).

Reference được giữ tại hệ thống riêng có access control. Không commit reference, consent record, raw personal image hoặc reconciled answer key vào student repo trước mốc khoá nhãn.

