# Independent review 2397

**Result:** PASS_SCOPED.

Candidate source and artifact hashes match the receipt. The pinned body ranges and instruction bytes are retained as specified in touch-row-sequence-item-state-5ecc-2394/001.

Independent isolated replay passes 3240 cases; output hash matches pinned replays.json.

The 5ECC body and FFFF00FF literal match source. Fixtures verify captured count, 28/44-byte layout selection, ordered masking, mode1 use of original word|FF00, mode2 use of masked word plus item byte9, and masked-only behavior for other 32-bit modes.

**Limits:** Pointers/counts and buffers are stable and separate; no aliasing or caller-wide effects are claimed. Private bounded evidence only; accepted:false.
