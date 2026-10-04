# P2-9073 independent scoped review

Status: PASS_SCOPED; accepted: false; status: partial.

- All 192 Thumb instructions covering 450 bytes at 0x530186..0x530348 and all 19 literal references match the locked image.
- The pseudocode retains the state-dependent branch order: state 0 starts a packet; state 1 chooses width and gathers header bytes before considering allocation; state 2 consumes payload and decrements remaining; state 3 clears busy and dispatches only when the packet pointer is nonnull.
- Allocation branches are width/type-specific, and branches that do not allocate leave prior P intact. Length/header arithmetic is explicitly low16 where the instructions truncate. Return values distinguish early abort/original length from exhaustion/consumed count; POP returns modified saved R3 as R1 with original high half preserved.

Limitations:

- Child allocator, capacity check and dispatch contracts are outside this extent. Old-pointer reuse, unvalidated pointers and callback mutation are retained as observed paths; no cleanup, atomicity, full parser protocol, or physical transport claim.
