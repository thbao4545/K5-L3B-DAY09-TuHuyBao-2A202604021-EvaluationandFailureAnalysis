# Mã nguồn Lab 9 — Evaluation & Failure Analysis (LogiX-VN)

Chạy các lệnh dưới đây từ thư mục `src/`. Lab 9 dùng agent tham chiếu `swarm` của Day 8, MockLLM và kết quả judge lưu sẵn, nên có thể chạy offline sau khi cài thư viện. Giữ nguyên `lab8/` để baseline và các variant dùng cùng runtime.

## Cài đặt và kiểm tra

Dùng Python 3.11–3.13. Nếu đã có `.venv`, kích hoạt môi trường đó và chạy từ bước cài thư viện.

**Windows PowerShell**

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt -r requirements-lab9.txt
python -m lab9.smoke
```

Nếu PowerShell chặn script kích hoạt, dùng `.\.venv\Scripts\python.exe` thay cho `python` trong các lệnh.

**macOS / Linux**

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt -r requirements-lab9.txt
python -m lab9.smoke
```

Smoke test in `M0 PASS` khi import được các thư viện và tìm thấy fixture cần thiết. Nếu checkout chưa có `lab8/` hoặc `data/public_claims.jsonl`, xem hướng dẫn lấy mã nguồn Day 8 trong [README gốc](../README.md).

## Cấu trúc

| Đường dẫn | Nội dung |
| --- | --- |
| `lab8/`, `data/public_*` | Runtime, agent tham chiếu và fixture công khai của Day 8 |
| `lab9/evalset.py`, `data/eval/` | Build và kiểm tra eval set. Mỗi phiên bản có file item JSONL và file nhãn JSON riêng |
| `lab9/graders.py`, `lab9/stats.py`, `lab9/judge.py` | Chấm trace, tính thống kê và đối chiếu judge replay với nhãn người |
| `lab9/eval.py`, `lab9/gate.py` | Chạy eval, xuất report JSON và so sánh với baseline |
| `lab9/trace_case.py`, `lab9/variants.py`, `lab9/mutation.py`, `lab9/traps.py` | Phân tích một trace, chạy variant, đo nhiễu A/A và kiểm tra tính toàn vẹn của report |
| `config/metric_spec.yaml`, `config/metric_spec_v2.yaml`, `config/fm_map.yaml` | Metric, ngưỡng gate, seed và ánh xạ cơ chế adversarial sang failure mode |
| `tests/`, `grader_audit/` | Test runtime và eval, cùng [bài kiểm toán grader](grader_audit/README.md) |
| `harness_map.eval.yaml` | Mẫu cấu hình mục `eval` cho `harness_map.yaml` |
| `reports/` | Report sinh bằng lệnh eval hoặc mutation. Xem [hướng dẫn nộp](../SUBMISSION.md) |

## Core (M0–M4)

`python -m lab9.evalset --build` tạo eval set v1 từ 14 claim công khai và lưu nhãn vào `data/eval/labels_v1.json`. Khi đã có eval set, dùng `--check` để kiểm tra. Gắn `failure_modes` theo [taxonomy](../docs/failure_taxonomy.md) và giữ nhãn tách khỏi item.

```text
python -m lab9.evalset --check
python -m lab9.judge --csv data/eval/judge_tone_public.csv --audit 5
python -m lab9.trace_case --shape seeded_regression --claim C-002 --seed 11
python -m pytest -q -m student -o addopts= -k "lab9 and not advanced"
```

Lệnh judge in Cohen’s κ, precision, recall và các ví dụ bất đồng để đối chiếu với [judge audit](../docs/judge_audit.md). Lệnh trace hỗ trợ tìm bước sai đầu tiên của một cặp claim và seed. Tùy chọn `-o addopts=` bỏ bộ lọc mặc định của pytest để chạy test có marker `student`.

Sau khi hoàn thành M1–M3, sinh baseline `swarm` rồi chấm hai variant với cùng eval set, metric spec và seed.

```text
python -m lab9.eval --shape swarm --spec config/metric_spec.yaml --out reports/baseline_v1.json
python -m lab9.eval --shape fixed --spec config/metric_spec.yaml
python -m lab9.gate --pr reports/eval_fixed.json --baseline reports/baseline_v1.json --spec config/metric_spec.yaml
python -m lab9.eval --shape seeded_regression --spec config/metric_spec.yaml
python -m lab9.gate --pr reports/eval_seeded_regression.json --baseline reports/baseline_v1.json --spec config/metric_spec.yaml
```

Kết quả cần đạt là `fixed` trả exit 0 và `seeded_regression` trả exit 1 với `pass_rate` trong danh sách metric bị chặn. CI còn chấm report `swarm` của PR so với baseline. Xem [checkpoints](../CHECKPOINTS.md) và [eval card](../docs/eval_card.md) để ghi lại kết quả thực tế.

## Advanced và Expert (M5–M7)

Sau khi cập nhật `config/fm_map.yaml`, dùng `python -m lab9.evalset --v2 --build` để ghép adversarial pack vào v1. V2 dùng baseline riêng vì gate kiểm tra mã băm eval set trước khi so sánh hai report.

```text
python -m lab9.evalset --v2 --check
python -m lab9.eval --shape swarm --spec config/metric_spec_v2.yaml --out reports/baseline_v2.json
python -m lab9.mutation --spec config/metric_spec_v2.yaml --aa 66,77,88,99,110
python -m lab9.mutation --spec config/metric_spec_v2.yaml --baseline reports/baseline_v2.json
python -m lab9.eval --shape slice_regression --spec config/metric_spec_v2.yaml
python -m lab9.traps --pr reports/eval_slice_regression.json --baseline reports/baseline_v2.json --spec config/metric_spec_v2.yaml
python -m pytest -q -m student -o addopts= -k advanced
```

Dùng A/A để quan sát độ dao động khi giữ nguyên agent và đổi bộ seed. Scorecard kiểm tra gate chặn các variant lỗi và cho qua `fixed` cùng `honest_refactor`. Lệnh `traps` dùng report `slice_regression` đã bị gate chặn để thử các kiểm tra toàn vẹn. Hiện `slice_check` và `integrity_check` trong `lab9/gate.py` vẫn còn TODO. Spec v2 còn thiếu các slice bắt buộc, ngưỡng `pass_hat_5` và metric FM-08.

## Report nộp bài

Giữ report do chương trình sinh ra. Git bỏ qua report JSON theo mặc định. Khi nộp, chạy `git add -f reports/*.json` trong `src/` để đưa các report cần chấm vào commit. Danh sách file và quy trình PR nằm trong [SUBMISSION.md](../SUBMISSION.md).
