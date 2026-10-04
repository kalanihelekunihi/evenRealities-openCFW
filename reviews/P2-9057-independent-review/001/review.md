# P2-9057 independent scoped review

Status: PASS_SCOPED; accepted: false; status: partial.

- The four instructions in 0x473940..0x47394A match the pinned image: MRS PRIMASK to R0, CPSID i, BX LR, followed by a separate BX LR leaf.
- The first leaf returns the observed prior PRIMASK in R0 while interrupts remain masked; the second leaf returns incoming R0 unchanged. Ring callers restore PRIMASK from the saved first-leaf result.

Limitations:

- This describes architectural instruction/register effects only; it does not prove physical interrupt delivery or concurrency behavior. This helper is distinct from the nesting-byte gate.
