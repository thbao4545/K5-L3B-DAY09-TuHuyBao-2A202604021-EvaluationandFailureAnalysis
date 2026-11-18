# Eval card ? LogiX-VN refund agent

Baseline E-swarm-20261118-f97e, fixed E-fixed-20261118-f97e, regression E-seeded_regression-20261118-f97e. Eval set SHA f97e8e0654f6, v1, 14 item ? 5 seed (11, 22, 33, 44, 55), ngu?n Lab 8 public v? nh?n t?ch ri?ng. Runtime MockLLM, metric spec v1.

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

Gate ch?p nh?n fixed v? ch?n seeded_regression ? pass_rate. V?i pass_rate, paired bootstrap ? fixed?baseline = +0.014, CI 95% [0.000, 0.043]. C?c ng??ng v? metric ??y ?? n?m trong config/metric_spec.yaml.

Judge tone ??t ?=0.757, P=0.857, R=0.800. Helpful kh?ng ??t ? v? recall. Xem [judge audit](judge_audit.md). Case [C-002@11](trace_case.md) ghi nh?n event ??u ti?n l?m sai d? ki?n.

V2 d?ng E-swarm-20261118-c9eb, SHA c9ebfdeaaad0, 28 item ? 5 seed. Baseline pass_hat_5=0.8929. So s?nh A/A gi?a hai b? seed tr?n MockLLM cho ?=0 ? c?c metric ???c in. Ch?n s?n 0.80 cho pass_hat_5, ngo?i d?i nhi?u quan s?t ???c. Slice money_movement b?t slice_regression. Slice adversarial theo d?i c?c claim t?n c?ng. Bug ch? xu?t hi?n ? 1/3 seed kh?ng ???c ph?t hi?n ?n ??nh v?i 5 seed.

Gi?i h?n g?m MockLLM, ch? 14 item v1, judge replay c?ng khai v? ch?a ?o ng??i d?ng th?t. Ch? s? h?u eval c?n ?i?u tra m?i gate exit 1. Khi thay ??i t?p item, t?ng eval-set version v? t?o baseline m?i.
