# Packed PPG sample accessors in C

The HR, HRV and SpO2 packed cache accessors in
`runtime/native_health_latest_samples.c` now use C instead of three naked
assembly bodies. They retain null/availability checks, the native unaligned
word load/store, and the trailing byte or halfword reload/store. Packed,
may-alias volatile types preserve access widths and ordering without assuming
aligned buffers. HR/SpO2 availability is a byte at offset 75; HRV uses a
halfword at offset 147. Payloads are five or six bytes respectively.

[Machine-readable evidence](ppg-packed-c-review.json) binds sources, full build,
probes, controls, disassembly, qualification and hybrid reports by SHA-256.
There are 1,290 paired stock/C cases (2,580 executions), including the unchanged
expanded wrappers calling the real C leaves. Cases cover null/unavailable data,
high-byte-only HRV availability, unaligned outputs, seeded cache contents,
interrupt masks and overlapping source/output ranges. Ordered RAM read/write
addresses, widths and values compare, as do guarded cache/output bytes,
returns, SP, callee-saved registers and masks. Expanded-wrapper R2/R3 return
observations are also checked; other caller-clobbered words/flags and private
stack accesses are excluded. Controls that truncate HRV availability to a byte
or preload the trailing field before the first output store are rejected.
Stable cache contents are assumed; asynchronous sensor updates, malformed
pointers and physical sensor operation remain unverified.

The three expanded assembly wrappers remain byte unchanged, as do every other
compiled object. Their private frame behavior is outside this C conversion.
The reset decoder's ambient-register bridge was inspected but retained because
ordinary C forwarding would not establish its raw register-seed contract.

REA's default Ghidra database does not expose procedures at these three leaf
entries. Its recorded errors establish no procedure-coverage credit. Local
Thumb disassembly and execution against the locked image provide the instruction
and behavioral evidence; no G2 corpus gate advances.

All 573 R1 units compile without failures or duplicate strong symbols. Imports
remain 179 application and 34 bootloader. Five qualification profiles match only
the three unchanged symbolic-assembly wrappers; no new C leaf qualifies. Those
wrapper-only candidates are recorded but not promoted as part of this C-leaf
change. The canonical plan remains at 3,857 source-built bytes, 642,303 executable
pull-through bytes and 248 resource bytes. The hybrid still equals the locked
application byte for byte. Full source linking, source completeness and physical
operation remain unfinished.
