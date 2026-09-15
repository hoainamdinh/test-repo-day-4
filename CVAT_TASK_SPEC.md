# CVAT task spec — Day 4 Lane S

Lane S bao gồm **hai task**: **task A** (20 ảnh, `person`) và **task B** (5 ảnh, `hand`+`face`). Xem `STARTER_ALIGNMENT.md` mục 2.

## Environment (chung)

- Dùng đúng CVAT sẽ phục vụ cohort; ghi version và cách deploy (app.cvat.ai hay Docker self-hosted) vào `PILOT_RUN_SHEET.md`.
- Task type: Images, **Shape mode**. Track mode làm export sai schema.
- Skeleton không sửa được sau khi task đã tạo — preflight xong mới bấm Submit.

---

## Lane S — một project, **hai task**

Baseline kỹ thuật yêu cầu **hai task CVAT riêng**, không phải một task gánh cả ba skeleton:

```text
Project  DAY04-STARTER-DRYRUN        ← 3 skeleton label dùng chung
├── Task A  20 ảnh train             → chỉ vẽ `person`  → export COCO Keypoints 1.0
└── Task B  5 ảnh chọn từ task A     → chỉ vẽ `hand`+`face` → export riêng
```

Task B là một task CVAT thứ hai, không phải thêm label vào task A. Lý do tách: topology 21 và 5
điểm không cùng category với bộ 17 điểm, và task B có **export riêng** đặt vào
`annotations/face_hand/`. Gộp chung sẽ làm hỏng contract 29 annotation/51 số của task A.

### Label chung cho cả project

| Label | Type | Sublabel | Dùng ở |
| --- | --- | --- | --- |
| `person` | skeleton | 17 tên COCO, đúng thứ tự | **task A** |
| `hand` | skeleton | 21 tên MediaPipe (`wrist`, `thumb_cmc` … `pinky_tip`) | **task B** |
| `face` | skeleton | 5 tên (`left_eye`, `right_eye`, `nose`, `mouth_left`, `mouth_right`) | **task B** |

Hai đường tạo label, cả hai đều phải chứng minh được trên CVAT Docker (D-07):

1. **Raw tab** — dán nguyên `labels_day4.json` từ `$STARTER_ASSETS_DIR` vào tab *Raw* khi tạo
   project. Đây là đường mặc định, tạo cả ba skeleton một lượt; hai task kế thừa label của project.
2. **Skeleton Configurator** — upload `skeleton_person_17.svg`, `skeleton_hand_21.svg`,
   `skeleton_face_5.svg` từ cùng thư mục đó.

`$STARTER_ASSETS_DIR` là thư mục chứa `labels_day4.json` trong checkout starter;
`scripts/check-starter-alignment.py` tự tìm và in đường dẫn thật ra.

`From model → Human pose estimation` **không có** trên CVAT self-hosted trần: nó cần Nuclio, và
`/api/lambda/functions` trả 503. Đừng dạy đường này nếu lớp chạy Docker.

### Task A — 20 ảnh, chỉ `person`

- Images: 20 file trong `dataset/images/train` của starter (đúng 20, không kèm test).
- Số người kỳ vọng: **29** — 12 ảnh 1 người, 7 ảnh 2 người, 1 ảnh 3 người (`train_13`).
- Chỉ dùng label `person`. Không vẽ `hand`/`face` ở task này.

Expected archive contract — task A:

- Export **COCO Keypoints 1.0** (không phải COCO 1.0, không phải YOLO 1.1).
- 20 image record, basename khớp `train_01.jpg` … `train_20.jpg`.
- Tổng **29** annotation `person`; ảnh nhiều người có đúng số annotation tương ứng.
- Mỗi `keypoints` đúng 51 số; `num_keypoints == count(v > 0)`.
- Category `person` có 17 keypoint và 19 skeleton edge.
- Sau khi chạy `tools/coco_kp_to_yolo_pose.py`: 20 file `.txt`, mỗi dòng **56 số**.

### Task B — 5 ảnh, chỉ `hand` + `face`

- Task CVAT **thứ hai**, cùng project, tên đề xuất `DAY04-STARTER-DRYRUN-FACEHAND`.
- Images: 5 ảnh chọn lại từ bộ 20 — ưu tiên ảnh thấy rõ bàn tay trên vô lăng.
- Chỉ dùng `hand` (21 điểm) và `face` (5 điểm). Không vẽ lại `person`.
- Export **riêng**, đặt vào `annotations/face_hand/`. Không trộn vào export của task A.
- Bộ này **không** được chấm bằng OKS — không có gold cho nó. Nó nằm trong reviewer checklist.
- Thời lượng thật của task B là số đo của gate G-03 (T-08). Việc nó là **core hay stretch** do
  owner chốt sau khi có số đo, không tự kích hoạt — `STARTER_ALIGNMENT.md` mục 0, D-06.

### Multi-person checklist — task A (gate G-02)

Đây là phần pilot cũ chưa từng chạm, nên phải kiểm thủ công:

1. Trên `train_13` (3 người) tạo đủ 3 skeleton `person` riêng, không nối xương chéo giữa hai cơ thể.
2. Save → reload trang → mỗi skeleton vẫn giữ đúng định danh và thứ tự trong sidebar.
3. Export → đếm đúng 3 annotation cho image đó, không gộp, không trùng.
4. Với mỗi ảnh 2 người: kiểm `left_*` theo **cơ thể từng người**, không theo màn hình.
5. Đổi thứ tự vẽ (vẽ người bên phải trước) rồi export lại — thứ tự annotation không được làm đổi mapping người.

Hai lỗi cần đo vì evaluator của baseline phạt nặng: `nham_nguoi` (khớp của người A gán cho
người B) và `dao_trai_phai`.



---

## Visibility mapping — round-trip bắt buộc cho cả hai lane

| CVAT point state | COCO expected |
| --- | ---: |
| Visible | `v=2` |
| Occluded | `v=1` |
| Outside | `v=0` |

Technical POC phải tạo ít nhất một point ở mỗi state, save/reload, export COCO Keypoints 1.0 rồi
kiểm JSON bằng validator. `Hidden` chỉ thay UI và không phải annotation state bền vững — điểm vẫn
xuất ra `v=2` ở tọa độ cũ mà không có cảnh báo.
