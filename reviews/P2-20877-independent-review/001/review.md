# P2-20877 independent review

Status: **partial / unaccepted**.

Fresh replay passed for 112 bytes at 0x47D27C..0x47D2EC; pinned image/source hashes and tiling match. The inherited full R6 value is preserved. Both diagnostic branches read the runtime flag byte independently for bit3 then bit2, placing bit3/bit2 in the stack/register arguments in the observed order; the mask branch repeats those reads rather than reusing a snapshot. These are four distinct byte observations across branches, and status queries are separate. No flag stability assumption is made; continuation remains pending.
