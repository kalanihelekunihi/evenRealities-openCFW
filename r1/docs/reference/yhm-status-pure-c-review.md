# YHM2710 charger status ordinary C entry

`r1/src/application/board/native_yhm_status.c` replaces the naked entry and saved-R3 worker with one C function. The ready check, register-six one-byte read, upper-nibble extraction and special status 14 → 17 remain. Raw read return words are ignored, as stock. No new persistent state is introduced.

The read byte starts at `0xc0`. A provider that writes no byte yields status 12, matching the existing not-ready result. This replaces saved caller-register history with a deliberate fallback; it does not establish hardware read success. The existing charge-state mapper maps status 12 to result 1, including for the stock not-ready path. This policy is separate from stock/C equivalence for written bytes.

REA bytes match the official application. Direct execution passes **27,648 stock/C comparisons** across all 256 register bytes, raw readiness/status words, caller scratch patterns and three roots: status, actual charge-state mapper and public charger getter. Another **6,912 unwritten-read cases** verify the defined fallback. All 96 reachable stock code bytes execute; the 16-byte switch table is data. Provider writes beyond the requested byte and incidental caller-clobbered outputs are excluded.

An additional **27,648 stock/C comparisons and 6,912 unwritten-read cases** execute the actual C register frontend and transport. The fixture verifies register six, one-byte length, live request-buffer destination and the IRQ-release → bus-acquire → read-transfer → bus-release sequence. Readiness and registry device operations remain modeled; no physical charger or single-wire timing proof is claimed. The normal callback field is zero in this integration fixture; nonzero completion callbacks remain outside this receipt's coverage.

Three compiled defects are rejected: wrong nibble, lost special status and wrong unwritten-read fallback. Both fixtures verify callee-saved integer/FP registers, SP, caller stack and interrupt masks, with caller-clobbered integer/FP registers overwritten by modeled callees.

The open-toolchain report `build/sources-goal-r1-yhm-status-pure-c/report.json` compiles all **855 units** and completes application/bootloader relocatable compositions. All **844 other nongenerated objects** remain identical to the prior ladder build. Imports remain **62 application / 22 bootloader**. R1 manifest validation passes. Source-plan selections are unchanged. Final application linking/startup and physical charger operation remain unverified.

[Machine receipt](yhm-status-pure-c-review.json) binds sources, REA and ignored probe evidence in `build/goal-r1-yhm-status-pure-c/`.
