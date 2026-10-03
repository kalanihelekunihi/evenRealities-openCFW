# Independent review 2417

**Result:** PASS_SCOPED.

Candidate source and artifact hashes match the receipt. The pinned body ranges and instruction bytes are retained as specified in touch-processing-row-clamp-5bc0-2414/001.

Independent isolated replay passes 648 cases; output hash matches pinned replays.json.

Original 5C02/5BC0 verify type7 bypass, primary limit and fresh valid/count fields, secondary-limit reload at the split, sticky cap behavior, ordered conditional writes and status/register assertions.

**Limits:** Stable fields during iteration; mutable-pointer/count behavior and actual producer output remain unresolved. Private bounded evidence only; accepted:false.
