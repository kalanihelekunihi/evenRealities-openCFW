# P2-9043 independent scoped review

Status: PASS_SCOPED; accepted: false; status: partial.

- Fresh isolated replay passed all 262,144 original-byte lookup cases: every 16-bit ID under four table patterns and nonzero high-word aliases, including duplicate keys and 0xFFFF.
- The independent first-match oracle agrees with returned record pointers or null; preserved register and stack/stop-PC checks passed.

Limitations:

- Synthetic records and SRAM only; malformed pointers, concurrent table mutation, and physical behavior are outside scope.
- No global table bound, active-state semantics, or firmware-wide behavior is inferred.
