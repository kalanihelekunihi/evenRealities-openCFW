# Independent review P2-18493

Status: partial, unaccepted. No source or gate changes.

Fresh GNU replay confirms the 70-byte continuation `0x4605D4..0x46061A`; instruction and PC-reference manifests match. It inherits the 16-byte frame saved by the previous prefix. The first fresh `0x43D0CE` result controls the bit-1 path. When set, the code writes the literal at `0x461040` to SP4 and 347 to SP0, then calls `0x43D574`. Otherwise, it makes a fresh bit-0 query and conditionally a separate fresh bit-2 query; the selected route calls `0x43CE9E` with the listed arguments.

The shared path sets R0 to zero and unconditionally stores zero through the retained global address in R4. POP then loads SP0/SP4 into R0/R1 and restores original R4/PC; it does not return the clear or any child result. Those stack slots still contain saved incoming R2/R3 unless diagnostics overwrote them; the first diagnostic overwrites both, the second overwrites SP0 only. The prior guard-failure path skips the clear and child calls, while a zero result from `0x49292E` enters the clear path directly, bypassing this second diagnostic.

Fresh mask calls and stack-slot aliasing were checked. Padding is excluded; child contracts and global ownership remain unresolved.
