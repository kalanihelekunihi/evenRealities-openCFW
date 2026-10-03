# Independent review 2455

**Result:** PASS_SCOPED.

Candidate: `g2/build/pseudocode-first/20260930T190500Z/analysis/touch-dispatch-measurement-mode-four-matrix-2454/001`. Receipt SHA-256 `15a421c78941ff196c905df26afac05250e082eabace5776945bc3aba2c7c350`; all declared replay, pseudocode, and disassembly hashes match. The 12 listed code ranges rehash to the pinned source image `371d8a61b659a33b4cad4a7d892e144aba8263ae59497b4f658afc5b0c430f87`.

I ran the candidate harness in an isolated output directory. All 576 cases pass. They cross nine prior mode-byte values (0–7 and 255) with the existing 64 measurement fixtures. The executed chain includes original 6AC0 and the dispatcher, reset, status wait, start/loader, budget, poll, scaler, and divider code; no firmware routine is replaced. The assertions cover exact mode-call arguments, the optional cfg+115 clear, sample-write gating, ordered side effects, arithmetic and poll/delay observations, aggregate status, and R4–R11/SP.

The request-four path tests equality against old mode 4 before the non-equality rejection: old mode 4 returns zero without clearing cfg+115, while the other tested old modes clear that byte and return 1 without storing a replacement mode or entering transition children. A nonzero poll remainder preserves that result; timeout replaces it with 256 and suppresses sample writes. The dispatcher’s aggregation is checked against those outcomes.

**Limits:** This packet does not test request-two transitions or other dispatcher modes, and its readiness/sample hooks model hardware inputs. It does not establish physical register behavior or timing, nor does it close prior literal/seam ownership questions. Bounded private evidence only; accepted:false, no canonical admission.
