# Independent review P2-5197

**Status:** PASS_SCOPED  
**Accepted:** false

Source-pinned isolated replay passes for substring and byte-search bodies. The substring path loads the first needle byte, searches candidate bytes, advances the needle before its next load, and restarts from the next candidate on mismatch. The character helper skips zero hay bytes and returns the matching pointer or zero; load/comparison ordering is preserved.

## Limits

Null/bounds/volatile/fault behavior and direct character-zero cases are not established. Stable-memory algorithm interpretation only; private partial, accepted:false.
