# Judge audit

Chạy từ `src/` bằng `python -m lab9.judge --csv data/eval/judge_tone_public.csv --audit 5` và lặp lại với `judge_helpful_public.csv`. PASS/FAIL theo nhãn trong CSV.

| Tiêu chí | n | κ | Precision | Recall | TP / FP / FN / TN | Quyết định |
|---|---:|---:|---:|---:|---|---|
| tone_ok | 100 | 0.757 | 0.857 | 0.800 | 24 / 4 / 6 / 66 | Dùng cho tone |
| helpful | 100 | 0.375 | 1.000 | 0.300 | 9 / 0 / 21 / 70 | Loại khỏi gate |

Ngưỡng là κ ≥ 0.6, precision ≥ 0.8 và recall ≥ 0.7. Rogan–Gladen cho tỉ lệ lỗi hiệu chỉnh 0.30 ở cả hai bộ. Helpful bỏ sót 21 trường hợp lỗi nên recall quá thấp.

| Case | Judge | Người | Quyết định chỉnh rubric cho vòng đánh giá tiếp theo |
|---|---|---|---|
| H-008 | PASS | FAIL | Thêm ví dụ FAIL cho “nha” trong thông báo hoàn tiền chính thức. |
| H-017 | PASS | FAIL | Thêm ví dụ FAIL khi dùng “bạn ơi” và “nha” trong cùng thông báo. |
| H-029 | PASS | FAIL | Thêm ví dụ FAIL cho chỉ dẫn “không cần nhắn thêm” thiếu lời giải thích. |
| H-042 | FAIL | PASS | Thêm ví dụ PASS cho câu có thời gian hoàn tiền và kết thúc lịch sự bằng “ạ”. |
| H-051 | FAIL | PASS | Thêm ví dụ PASS có từ “refund” khi câu còn lại rõ ràng và lịch sự. |

Các thay đổi là bản đề xuất cho rubric tiếp theo, suy ra từ nhãn hiện có và cần người gán nhãn xác minh. Dữ liệu là replay công khai, cần tập held-out với nhãn người mới.
