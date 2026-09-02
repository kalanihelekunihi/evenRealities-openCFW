# G2 bootloader runtime startup tail source closure

Date: 2026-09-01

The prior `0x0043297C..0x004329BC` unresolved span contained two functions,
not one: a 30-byte runtime dispatcher at `0x0043297C` and a 32-byte
constructor-array walker at `0x0043299C`, separated by two alignment bytes.
The independent 14-byte terminal service loop at `0x004329C4` is also closed.

Both reviewed Arm compilers reproduce all 76 executable bytes exactly after
five strict call relocations. Apollo-main analogues at `0x005E4294`,
`0x005E42B4`, and `0x005E42DC` have identical instructions; the constructor
walker is byte-for-byte exact, while the dispatcher and terminal loop differ
only in image-specific call displacements. The external eight-byte
constructor-table literal pool remains separately retained.

Portable C models verify conditional constructor dispatch, ordered init-array
iteration, platform-init handoff, status preservation, and bounded terminal
service calls. Actual reset-to-runtime handoff and non-returning terminal-loop
behavior are **blocked by unavailable physical evidence**. No MMIO, flashing,
reset, or completeness claim occurred.
