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

V2 dùng `E-swarm-20261118-1ef6`, SHA `1ef614d16d06`, 28 item × 5 seed. Baseline pass_hat_5=0.8929. So sánh A/A giữa hai bộ seed trên MockLLM cho Δ=0 ở các metric được in. Sàn pass_hat_5 là 0.80, ngoài dải nhiễu quan sát được. Slice money_movement bắt slice_regression. Slice adversarial theo dõi claim tấn công. Bug chỉ xuất hiện ở 1/3 seed không được phát hiện ổn định với 5 seed.

Giới hạn gồm MockLLM, 14 item v1, judge replay công khai và chưa đo người dùng thật. Chủ sở hữu eval cần điều tra mỗi gate exit 1. Khi thay đổi tập item, tăng eval-set version và tạo baseline mới.
