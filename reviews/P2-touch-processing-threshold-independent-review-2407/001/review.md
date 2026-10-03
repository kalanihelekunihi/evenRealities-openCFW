# Independent review 2407

**Result:** PASS_SCOPED.

Candidate source and artifact hashes match the receipt. The pinned body ranges and instruction bytes are retained as specified in touch-processing-threshold-5f6a-2404/001.

Independent isolated replay passes 576 cases; output hash matches pinned replays.json.

Original 5F6A/A6C0 fixtures verify row validity gate, cfg byte87 percentage, selector-zero parameter-halfword multiplication with 32-bit wrap, nonzero-selector bypass, and unsigned division by 100.

**Limits:** Stable valid fixture pointers; no index validation or broader configuration/physical claim. Private bounded evidence only; accepted:false.
