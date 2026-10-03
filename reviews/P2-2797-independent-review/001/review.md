# Independent review 2797 — current profile restore map

**Result: PASS_SCOPED.** The isolated verifier decoded all 31 original Thumb instructions over `[0x429DA4,0x429DF6)`. Source, body, and artifact hashes match. Literal resolution confirms control address `0x40020080`, current index pointer `0x20000150`, profile base `0x20026BA0`, high target `0x40020044`, and clear-byte address `0x200271BC`.

The listing verifies three separate current-index/profile reads, ordered bitfield replacements with fresh control reads, the final flag-byte clear, and return/register effects described in the candidate. The adjacent NOP after `0x429DF6` is excluded. This is static mapping only and does not establish dynamic pointer mutation, bounds, or caller ownership. The packet remains private `accepted:false` evidence.
