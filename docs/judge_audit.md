# Judge audit

Chạy từ `src/` bằng `python -m lab9.judge --csv data/eval/judge_tone_public.csv --audit 5` và lặp lại với `judge_helpful_public.csv`. PASS/FAIL theo nhãn trong CSV.

| Tiêu chí | n | κ | Precision | Recall | TP / FP / FN / TN | Quyết định |
|---|---:|---:|---:|---:|---|---|
| tone_ok | 100 | 0.757 | 0.857 | 0.800 | 24 / 4 / 6 / 66 | Dùng cho tone |
| helpful | 100 | 0.375 | 1.000 | 0.300 | 9 / 0 / 21 / 70 | Loại khỏi gate |

Ngưỡng là κ ≥ 0.6, precision ≥ 0.8 và recall ≥ 0.7. Rogan–Gladen cho tỉ lệ lỗi hiệu chỉnh 0.30 ở cả hai bộ. Helpful bỏ sót 21 trường hợp lỗi nên recall quá thấp.

| Case | Judge | Người | Ai đúng và vì sao (ghi chú người gán) | Quyết định chỉnh rubric cho vòng đánh giá tiếp theo |
|---|---|---|---|---|
| H-008 | PASS | FAIL | Người: xưng “em” và kết câu bằng “nha” quá suồng sã với khách; judge coi là thân thiện. | Thêm ví dụ FAIL: CSKH xưng “em” hoặc kết câu bằng “nha” trong thông báo hoàn tiền. Giọng thân thiện không thay cho cách xưng hô trang trọng. |
| H-017 | PASS | FAIL | Người: gọi khách là “bạn”, không phù hợp với khách lớn tuổi; judge coi là thân thiện. | Thêm quy tắc xưng hô: gọi khách là “anh/chị”, không dùng “bạn”. Dùng câu này làm ví dụ FAIL. |
| H-029 | PASS | FAIL | Người: “không cần nhắn thêm” là giọng ra lệnh; judge chỉ thấy “Dạ, vui lòng”. | Thêm quy tắc: từ lịch sự ở đầu câu không bù cho câu mệnh lệnh với khách. Dùng câu này làm ví dụ FAIL. |
| H-042 | FAIL | PASS | Người: câu ngắn nhưng đủ ý; judge phạt vì thiếu lời xin lỗi. | Ghi rõ: không bắt buộc xin lỗi khi đã hoàn tiền. Câu ngắn có số tiền và thời gian nhận tiền vẫn PASS. |
| H-051 | FAIL | PASS | Người: CS LogiX cho phép dùng “refund”; judge phạt vì là từ tiếng Anh. | Ghi rõ: “refund” là từ được phép. Không trừ điểm tone chỉ vì từ này. |

Cột “Ai đúng” lấy từ cột `note` của người gán nhãn trong `judge_tone_public.csv`. Mỗi thay đổi rubric nhắm vào đúng nguyên nhân trong ghi chú đó: xưng hô (H-008, H-017), giọng mệnh lệnh (H-029), yêu cầu xin lỗi không cần thiết (H-042) và từ được phép (H-051).

Các thay đổi là bản đề xuất cho rubric tiếp theo, suy ra từ nhãn hiện có và cần người gán nhãn xác minh. Dữ liệu là replay công khai, cần tập held-out với nhãn người mới.
