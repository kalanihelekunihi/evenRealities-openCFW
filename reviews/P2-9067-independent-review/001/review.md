# P2-9067 independent scoped review

Status: PASS_SCOPED; accepted: false; status: partial.

- Fresh isolated replay passed all 128 original-byte writer/ring/signal cases with the original gate and null wake path, comparing full buffers and state.
- The oracle preserves the observed behavior where a ring advance may reject after output bytes were written, yet signal and return-length behavior still occur; it also checks copy bytes beyond logical capacity where the code does so.
- Registers, output/state memory, signal fields, PRIMASK, SP, and PC assertions passed.

Limitations:

- Synthetic buffers/MMIO only. No physical transport delivery, capacity safety, concurrency, or application-level message interpretation is established.
