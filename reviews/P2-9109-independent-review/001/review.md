# P2-9109 independent scoped review

Status: PASS_SCOPED; accepted: false; status: partial.

- Fresh isolated replay passed all 800 original-byte fill cases spanning four destination alignments, 40 lengths, and five fill values.
- The independent full-buffer model and sentinels matched the backward fill extent for each case; returned pointer/value, preserved registers, SP, and PC checks passed.

Limitations:

- Only the selected bounded test lengths/values and valid synthetic memory are covered. Huge-length wrap, invalid pointers, MMIO, concurrency, and generic forward-fill equivalence are not established.
