# P2-21167 independent review

Status: partial / unaccepted. No source or gate changes.

Fresh replay passed for 0x4810B0..0x481142 (146 bytes); instruction and literal-reference outputs match. The frame saves R0–R8 and LR (40 bytes). The full pointer null check and UXTB mode bound precede mode-specific work. Modes 0/1 load the index, enforce the unsigned 224 bound, and call 0x480ED8 with the observed stack outputs; modes 2/3 skip that setup in this prefix. Bank selection uses a 16-byte stride and adds 112 only for selector 1 in the prefix address setup. The helper result is staged at SP8 before the mode dispatch. Mode 0 performs a fresh word read/clear/store and conditionally a second bank clear for selector 2. Remaining modes and unwind are unresolved.
