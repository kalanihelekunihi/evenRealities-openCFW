# Independent review 2647: handler index helper

**Result: PASS_SCOPED.** `accepted` remains false.

The candidate, source, body, and artifact pins match. The 28-byte table at `0x433498` matches the recorded bytes. I reran the replay in a fresh isolated directory; all 400 fixtures pass with the original copy helper and no function interception.

The original helper computes `(old >> 2) * 5 + (new >> 2)`, copies the table to its stack buffer, writes the selected byte, and returns 7 immediately for byte 26. The special pair overrides and byte-25 transition mapping match the decoded branches and fixture writes. Those transition categories also require both upper-word quotients to be below 5; the tested inputs 0 through 19 satisfy that bound. The frame and return assertions pass.

The helper does not guard table indices. Inputs outside the tested domain may read beyond the 28-byte table. Aliasing, null destinations, concurrent mutation, physical effects, and caller ownership remain unresolved. This is private scoped evidence, not canonical admission.
