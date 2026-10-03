# Independent review 2409

**Result:** PASS_SCOPED.

Candidate source and artifact hashes match the receipt. The pinned body ranges and instruction bytes are retained as specified in touch-processing-byte-search-original-threshold-2406/001.

Independent isolated replay passes 640 cases; output hash matches pinned replays.json.

Original 7580, 5F6A, A6C0 and 5F5E execute. Threshold values derive from cfg byte87 and requested parameter halfword; the independent search oracle uses the resulting threshold for candidate decisions.

**Limits:** Other search helpers are controlled; tested parameter/status patterns only. Private bounded evidence only; accepted:false.
