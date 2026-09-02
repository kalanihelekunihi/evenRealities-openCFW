# G2 bootloader unreferenced linked services source closure

Date: 2026-09-01

The complete mode-four wrapper at `0x00430AEC` and zero-table walker at
`0x00431E38` are MIT production C. Both reviewed compilers reproduce all 88
bytes exactly; Apollo-main analogues are byte-for-byte exact. Portable models
cover provider success/failure, absolute and relative table descriptors,
partial-word zeroing, termination, and bounds rejection.

No direct or stored bootloader ingress exists for either linked function, so
they are not claimed as live capabilities. Any platform path that may invoke
them outside the authenticated image is **blocked by unavailable physical
evidence**. No flashing, reset, or completeness claim occurred.
