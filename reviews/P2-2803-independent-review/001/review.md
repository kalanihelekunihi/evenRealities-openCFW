# Independent review 2803 — handler 0 normal chain

**Result: REVISE_METADATA.** The 64-fixture isolated replay passes, and the candidate artifact hashes are internally consistent. However, the receipt does not hash the handler0 body: it declares `846627b1f8b071b4cc86024dfedbe1e5e1e585a0b2f9891186d3d2b84d94f3be`, but the actual 470-byte, 160-instruction interval `0x427E84..0x42805A` hashes to `1a259e009f8dfe9641a5c1062b41e1cc32eab8b34c6f919a19485e7897a37310`. The candidate replay code’s receipt line hashes unrelated range `0x429C46..0x429D9E`. Refresh the body range/hash and dependent receipt hashes in an append-only correction before relying on this packet’s body binding.

The replay supports only its stated normal-path fixtures: control bit 0 clear and indices 0/1. Wait/service and equal-index branches, other inputs, hardware effects, concurrency, and incoming ownership remain untested or unresolved. No canonical admission.
