# Independent review 2477

**Result:** PASS_SCOPED.

Candidate: `g2/build/pseudocode-first/20260930T190500Z/analysis/touch-mode-two-fresh-config-commit-2476/001`. Receipt SHA-256 `2955be8799de33600959b8083e8bc1a9b371ef7c38c93813628244a85f0a6766`; all declared file hashes and five body-span hashes validate against the pinned source image.

The isolated replay passed all 160 cases. Original 6AC0, list/pair wrappers and 8FD0 run; only 5FC6 is controlled. The first pin call redirects ctx.word8 to a distinct config after the original config’s byte115 clear. Assertions confirm the old config retains its original byte85, the replacement config’s byte115 remains `0xCC`, and successful loader completion stores mode2 through a fresh ctx.word8 load into the replacement config. Unsupported selectors return 64 without a mode store. The parent checks exact write destinations, loader/port effects, status, and R4–R11/SP.

**Limits:** The config-pointer mutation is supplied by a controlled child, not established as normal firmware behavior. Other root/table lifetimes are bounded to the fixture’s pointer setup. MMIO/factory inputs are modeled, and physical hardware, general aliasing, and further mutations remain unresolved. Private evidence only; accepted:false, no canonical admission.
