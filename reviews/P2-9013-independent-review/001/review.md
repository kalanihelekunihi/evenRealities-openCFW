# P2-9013 independent scoped review

Status: PASS_SCOPED; accepted: false; status: partial.

- The packet receipt pins the expected firmware and current scope, replay, and result hashes; its recorded 24 original-instruction cases cover three fill patterns, four event-byte values, and both mask inputs.
- The expected memory model records 0x785250 at other+60 as the published flash-table pointer; the callback slot at other+88 is distinct. The four table words at 0x785250 match the pinned image bytes.

Limitations:

- I could not independently rerun the fixture because Unicorn is unavailable in this environment. I checked the recorded results and replay logic, so this does not claim a fresh emulator replay.
- Synthetic SRAM only; no concurrency, physical behavior, or broader initializer semantics.
