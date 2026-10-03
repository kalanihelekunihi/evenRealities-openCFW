# Independent review 2411

**Result:** PASS_SCOPED.

Candidate source and artifact hashes match the receipt. The pinned body ranges and instruction bytes are retained as specified in touch-processing-minimum-distance-leaves-5f34-2408/001.

Independent isolated replay passes 289 cases; output hash matches pinned replays.json.

Original 5F34 and 5F5E bodies match pinned ranges. Fixtures confirm unsigned minimum over captured item count, FFFFFFFF empty result, unsigned absolute difference, no writes/calls, and register/SP preservation.

**Limits:** Stable list geometry and tested values only; no pointer safety or caller contract beyond observed behavior. Private bounded evidence only; accepted:false.
