# P2-21171 independent review

Status: partial / unaccepted. No source or gate changes.

Fresh replay passed for 0x481230..0x4812F6 (198 bytes); instruction and literal-reference outputs match. Mode 3 executes up to seven unrolled OR updates per bank, with each new input read preceding the corresponding fresh target read. UXTB selector 1 skips the first bank, 0 skips the second, and other values use both. Accepted mode paths join at the SP8 helper-result reload and PRIMASK update, then return zero. Validation failures branch directly to the status return and bypass MSR. ADD SP,16 plus LDMIA of six saved registers (24 bytes) completes the 40-byte unwind.
