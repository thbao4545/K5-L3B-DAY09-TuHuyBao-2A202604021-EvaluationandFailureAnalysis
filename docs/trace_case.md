# Trace case ? C-002@11

Trong report E-seeded_regression-20261118-f97e, Lab 8 grader b?o status resolved != denied. Ledger ghi m?t kho?n 20.000 VND, trong khi nh?n y?u c?u kh?ng ho?n ti?n.

| B??c | Quan s?t |
|---|---|
| 1?2 | Handoff v? investigator l?y d? li?u ??n O-202. ??n ghi tr? 2 ng?y. |
| 3 | Event model_override ghi delay_days = 5, ghi ?? d? ki?n DB theo ticket. ??y l? b??c sai ??u ti?n th?y trong trace, thu?c FM-03. |
| 4?6 | Quote 20.000 VND v? reply n?i ?? ho?n. Ledger x?c nh?n ?? ho?n 20.000 VND. |

??i ch?ng fixed C-002@11 kh?ng c? override, quote b?ng 0, status l? denied v? ledger b?ng 0. DbFactKept b?t event override v? RefundAmountCorrect b?t s? ti?n sai. Case n?y n?m trong eval set v? report v?i c?ng claim v? seed. Trace kh?ng gi?i th?ch tr?ng th?i n?i b? c?a model.

Test h?i quy `test_c002_trace_override_and_fixed_control` trong `src/tests/test_lab9_graders.py` t?i hi?n c?c event v? ledger ?? quan s?t, x?c nh?n hai grader fail tr?n variant l?i v? pass tr?n ??i ch?ng.
