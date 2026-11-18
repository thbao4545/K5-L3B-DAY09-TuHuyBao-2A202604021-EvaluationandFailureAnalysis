# Eval card — LogiX-VN refund agent

Baseline `E-swarm-20261118-167b`, fixed `E-fixed-20261118-167b`, regression `E-seeded_regression-20261118-167b`. Eval set SHA `167b88307f34`, v1, 14 item × 5 seed (11, 22, 33, 44, 55), nguồn Lab 8 public và nhãn tách riêng. Runtime MockLLM, metric spec v1. SHA tính trên byte của file eval set với xuống dòng LF; `.gitattributes` giữ LF cho file này nên checkout trên Windows (`core.autocrlf=true`) cho cùng SHA với CI.

| Metric | Swarm | Fixed | Seeded regression |
|---|---:|---:|---:|
| approval_bypass | 0 | 0 | 0 |
| secret_leak | 0 | 0 | 0 |
| refund_amount_correct | 0.9857 | 1.0 | 0.8571 |
| pass_rate | 0.9857 | 1.0 | 0.7143 |
| reply_amount_correct | 1.0 | 1.0 | 0.7857 |
| status_correct | 0.9857 | 1.0 | 0.8571 |
| proposal_correct | 0.9857 | 1.0 | 0.7857 |
| pass_5 | 0.9286 | 1.0 | 0.7143 |
| cost_per_success | 49.567 | 48.7157 | 81.202 |

Gate chấp nhận fixed và chặn seeded_regression ở pass_rate. Với pass_rate, paired bootstrap Δ fixed−baseline = +0.014, CI 95% [0.000, 0.043]. Các ngưỡng đầy đủ nằm trong `config/metric_spec.yaml`.

Judge tone đạt κ=0.757, P=0.857, R=0.800. Helpful không đạt κ và recall. Xem [judge audit](judge_audit.md). [C-002@11](trace_case.md) ghi nhận event đầu tiên làm sai dữ kiện.

V2 dùng `E-swarm-20261118-1ef6`, SHA `1ef614d16d06`, 28 item × 5 seed. Baseline pass_hat_5=0.8929. So sánh A/A giữa hai bộ seed (11–55 và 66–110) trên MockLLM cho Δ=0 ở mọi metric. Sàn pass_hat_5 là 0.80, ngoài dải nhiễu quan sát được. Slice money_movement bắt slice_regression. Slice adversarial theo dõi claim tấn công. Bug chỉ xuất hiện ở 1/3 seed không được phát hiện ổn định với 5 seed.

Slice và metric bắt từng variant trong scorecard `lab9.mutation` (3/3, 0 báo nhầm):

| Variant | Kết quả | Metric/slice chặn |
|---|---|---|
| fixed, honest_refactor | merge | không có |
| slice_regression | block | `slice:money_movement/pass_rate`, proposal_correct; pass_rate trung bình vẫn trên sàn |
| flaky_regression | block | `pass_hat_5`, pass_rate, proposal_correct, `slice:money_movement/pass_rate` |
| seeded_regression | block | pass_rate, pass_hat_5, các metric số tiền/status, slice money_movement, adversarial và denial |

Vì sao nhiễu A/A khác 0 với LLM thật: MockLLM tất định theo hash của (seed, purpose, prompt), và agent swarm cho cùng kết quả trên cả hai bộ seed, nên Δ=0 ở đây không chứng minh dải nhiễu thật bằng 0. LLM thật lấy mẫu có nhiệt độ, nhà cung cấp đổi model hoặc hạ tầng, tool có thể timeout, nên chạy lại cùng item cho kết quả khác nhau và A/A cho Δ khác 0. Nếu sàn hoặc ngưỡng giảm nằm trong dải đó, gate sẽ chặn nhầm cả khi so baseline với chính nó. Vì vậy cần đo lại A/A trên LLM thật trước khi giữ sàn pass_hat_5 = 0.80.

Chống gian lận (M7): gate chặn cả 4 trap công khai bằng `integrity_check`. Hàm này kiểm tra metric NaN/inf, số dòng khác items × seeds, dòng trùng (item, seed), tập (item, seed) khác baseline, `evaluator_failures` khác rỗng kể cả khi mọi metric xanh, giá trị grader bị None, nhãn slice bị đổi, và ratchet ngưỡng khi có `--base-spec`. Các đường còn có thể lọt:
- Workflow CI không truyền `--base-spec`, nên một PR nới `config/metric_spec*.yaml` chỉ bị ratchet chặn khi chạy `lab9.traps` hoặc bộ chấm có truyền spec của main.
- Ratchet chỉ so ngưỡng khi `eval_set_version` giữ nguyên. Tăng version cùng lúc với nới ngưỡng thì không bị so.
- Baseline được đọc từ nhánh PR. `ci_check` bắt baseline sửa tay hoặc không phải swarm, nhưng một baseline chạy lại bằng script trên code đã hỏng trong cùng PR vẫn khớp với lần chạy swarm của CI.
- Report nộp tay mà sửa giá trị nhất quán (đổi dòng fail thành pass và tính lại metric) vẫn đúng cấu trúc. Chỉ chạy lại eval mới phát hiện được, và CI tự chạy lại eval nên ở CI đường này đã được chặn.

Giới hạn gồm MockLLM, 14 item v1, judge replay công khai và chưa đo người dùng thật. Chủ sở hữu eval cần điều tra mỗi gate exit 1. Khi thay đổi tập item, tăng eval-set version và tạo baseline mới.
