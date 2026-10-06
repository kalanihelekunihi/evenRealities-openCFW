# Independent review P2-18499

Status: partial, unaccepted. No source or gate changes.

Fresh GNU replay confirms the 178-byte branch `0x460694..0x460746`; instruction/reference manifests match. It inherits the 64-byte frame and retained R5 length/R6 input pointer. The first diagnostic branch makes fresh flag queries, uses SP8/SP4/SP0 local slots, and then calls `0x43D574`; the other decision path makes distinct bit-0 and conditional bit-2 queries before `0x43CE9E`.

The mode gate tests the full R5 value for exactly 2. On that path it reads both input bytes in order before testing the selector; the second byte replaces R4, while the first is narrowed to low 8 bits. A nonzero selector branches to the shared external epilogue. The zero selector triggers another fresh mask sequence and diagnostics, again writing locals rather than saved registers. The child calls receive the displayed live arguments. The final zero-selector route passes the low byte from R4 to the previously reviewed setter at `0x46036A`; the setter performs low-byte normalization followed by a fullword store.

The mode-four branch and external epilogue remain incomplete in this map. Child contracts are unresolved; no source/gate changes or larger routine claim.
