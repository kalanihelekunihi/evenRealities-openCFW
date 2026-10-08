# P2-21045 independent review

Status: partial / unaccepted. No source or gate changes.

Fresh replay passed for 0x47F3C6..0x47F46A (164 bytes); instruction/reference outputs match candidate. Both loops check unsigned count >=10000 before each fresh word read, so no read occurs after the 10,000th failed observation. The first helper result is ignored, followed by a separate word update and final distinct read; return is 4 only at the limit. The second function clears a different bit, spins on its own fresh bit-7 observations, and invokes the helper only on non-timeout completion; its result is ignored. POP stack slots differ between bypass/timeout and helper paths. No timing, cleanup, PRIMASK, or external helper claims inferred.
