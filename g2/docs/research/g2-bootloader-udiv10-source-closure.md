# G2 bootloader unsigned divide-by-ten source closure

The authenticated 188-byte entry at `[0x00415844,0x00415900)` is an unsigned
64-bit divide-by-ten helper with direct callers at `0x00415912` and
`0x004159B4`. Its shift/add/correction sequence is the division-free identity
implemented by `runtime_udiv10.c`; the source deliberately contains no `/` or
`%` operation that could introduce an unresolved compiler runtime dependency.

Host tests cover boundaries and 1,000 deterministic 64-bit values against the
native quotient. Apple clang 21 emits a relocation-free 106-byte Thumb leaf at
`0x004348D0` when machine outlining is disabled. The full stock span is
redirected by one non-linking `B.W` plus reviewed NOP fill. The Linux clang
profile independently reproduces the same leaf bytes and placement.

The helper is part of the 1,536-byte canonical bootloader overlay and the
150,136-byte canonical provider documented by the adjacent numeric closure.
Software closure is complete for this helper. Physical boot evidence is still
blocked because no authorized responsive G2 right temple is available; no
package was signed, transmitted, or flashed.
