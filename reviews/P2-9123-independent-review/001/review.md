# P2-9123 independent scoped review

Status: PASS_SCOPED; accepted: false; status: partial.

- All 74 instruction bytes match the pinned image.
- The drain loop dequeues until null, releasing nonnull packets, then sets record+26=1. Its return restores saved entry R2 into R0, with its low byte potentially overwritten by the queue-pop ID output; empty dequeue preserves that byte under the separately reviewed child behavior.
- The wrapper overwrites byte SP+2 within the saved R5 slot with 20, calls the callback with the stack pointer and callback word, drains, then creates/dispatches command 0x0C03. Its unusual POP returns stack words to R0-R2 rather than restoring R5-R7; callback stack mutation can alter those returned values.

Limitations:

- Callback is not null-checked, and its stack effects/ABI are not proven here. Command meaning and reset/error semantics are not inferred; no concurrency, physical, or whole-firmware claim.
