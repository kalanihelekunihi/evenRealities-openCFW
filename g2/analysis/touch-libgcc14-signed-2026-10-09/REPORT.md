# Signed division source rebuild and behavior

Unmodified exact-release GCC lib1funcs.S with its documented L_divsi3 selector
regenerates468stock bytes at `[0xA7D4,0xA9A8)`, matching the authenticated
_divsi3.o text before relocation too. The real weak zero hook is reused4bytes,
not counted again. Original BL relocation is checked against the stock target.
This is a new focused source comparator outside the54entryPDLcensus.

Signed division is460bytes `[0xA7D4,0xA9A0)`; signed divmod is8bytes
`[0xA9A0,0xA9A8)`. The old16bytedivmodrow overlaps the zero hook and alignment.
Original symbol rows remain unchanged. Compile/preprocessing/input/ELF/archive
hashes and actual commands are recorded in results.json.

200original-instruction fixtures cover both entrypoints and signed corner
operands.178normal cases verify truncation-toward-zero quotient and, for
divmod, signed remainder.20zero-divisor observations return quotient0 and
retain dividend as remainder. The two INT_MIN/-1 observations return
0x80000000 with remainder0. Those exceptional values are observed library
behavior, not defined C arithmetic or physical exception policy.

No real zero helper was stubbed; fixtures supply only registers/stack.
Original-results.json preserves outputs. No vendor full-build/debug/object
identity, whole firmware completeness, producer uniqueness or campaign
admission is claimed. Source/license provenance is reused from the reviewed
unsigned runtime source packet. Independent review of this new extent is pending.
