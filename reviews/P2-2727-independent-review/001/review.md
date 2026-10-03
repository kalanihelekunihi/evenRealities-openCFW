# Independent review 2727 — handler7 static map

**Result: PASS_SCOPED.** The isolated verifier decoded all 124 original Thumb instructions over `0x428920–0x428A78`; the source, body, and candidate artifact hashes match. The float constant resolves from the PC-relative load to `0x428C8C = 0x3F666666`.

The listing supports the described unsigned 32-bit subtraction before `VCVT.F32.U32`, multiplication by the binary32 literal, conversion back with `VCVT.U32.F32`, and temporary stack result. It also supports the packed return at stack offset 4, saved incoming R3 returned in R2, bounded/saturated target writes, timer/flag stores, and the stated profile-field updates. The adjacent literal pool at `0x428A78` is outside the owned body.

This review is limited to static source mapping; dynamic rounding, control-flow execution, and caller ownership are not established. Private `accepted:false` evidence only.
