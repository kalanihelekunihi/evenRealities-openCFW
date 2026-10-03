# Independent review 2951/001

**PASS_SCOPED**; `accepted` remains false.

I reran the original-instruction candidate in a fresh output directory: all 100 fixtures pass. The receipt source hash matches the locked flash image, and both body hashes match `[0x42BA00, 0x42BD8C)` and `[0x41B8EC, 0x41B8F8)`. The fixture grid is 10 operation words × 5 gate setups × 2 initial PRIMASK values. Modes 0–2 return 0 before the interrupt-save helper; invalid-magic mode 3 returns 1; valid-magic mode 3 with null option/input returns 6 for the listed low-byte operation values. Only the valid-magic cases invoke original `0x41B8EC`; PRIMASK restoration, no watched writes, R4–R12/SP, and the stop point are asserted.

This is bounded evidence for the tested error paths. Successful operation paths, changing or aliased reads, exceptions, and physical hardware effects remain outside scope.

Candidate receipt SHA-256: `12a25b79fed57fd8e4ed243852d0f53d42167637a5b88995d41b921dacb69225`.
