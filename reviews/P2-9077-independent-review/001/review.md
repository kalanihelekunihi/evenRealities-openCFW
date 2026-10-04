# P2-9077 independent scoped review

Status: PASS_SCOPED; accepted: false; status: partial.

- All 172 instructions across 0x530C88..0x530D34 match the pinned image; all literal references resolve to locked words.
- Enqueue compares low-byte type against 4 and 2 but both branches join the enqueue call, so no type is rejected in this range. It reads event id afterward and invokes signal; return is the latest child R0.
- The consumer routes dequeued packets according to packet/eventmask and queue fields. The stack slot seeded from entry R3 is reused as the queue-pop ID output, so its low byte may be overwritten; address getter at 0x530D30 is a separate function.

Limitations:

- Queue child ownership, release semantics, and unknown IDs remain unresolved; not every branch establishes deallocation. No queue validity, concurrency, physical signal delivery, or whole-firmware behavior is claimed.
