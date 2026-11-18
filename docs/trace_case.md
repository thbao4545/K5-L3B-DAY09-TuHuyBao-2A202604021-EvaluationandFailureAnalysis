# Trace case — C-002@11

Trong report `E-seeded_regression-20261118-f97e`, Lab 8 grader báo `status resolved != denied`. Ledger ghi một khoản 20.000 VND, trong khi nhãn yêu cầu không hoàn tiền.

| Bước | Quan sát |
|---|---|
| 1–2 | Handoff và investigator lấy dữ liệu đơn O-202. Đơn ghi trễ 2 ngày. |
| 3 | Event `model_override` ghi `delay_days = 5`, ghi đè dữ kiện DB theo ticket. Đây là bước sai đầu tiên thấy trong trace, thuộc FM-03. |
| 4–6 | Quote 20.000 VND và reply nói đã hoàn. Ledger xác nhận đã hoàn 20.000 VND. |

Đối chứng `fixed C-002@11` không có override, quote bằng 0, status là denied và ledger bằng 0. `DbFactKept` bắt event override và `RefundAmountCorrect` bắt số tiền sai. Test `test_c002_trace_override_and_fixed_control` trong `src/tests/test_lab9_graders.py` tái hiện event và ledger đã quan sát. Trace không giải thích trạng thái nội bộ của model.
