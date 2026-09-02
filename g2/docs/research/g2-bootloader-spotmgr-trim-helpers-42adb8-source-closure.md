# G2 bootloader SPOT-manager trim-helper source closure

The three contiguous exact Apollo-main candidates at `0x0042ADB8`,
`0x0042AE24`, and `0x0042AE6C` are source-owned register-trim helpers. Both
reviewed compilers reproduce all 228 bytes exactly. Portable tests cover the
10-bit trim arithmetic, headroom saturation, six/seven-bit profile fields,
two-bit mode field, enable gates, and restore gate. Live register behavior is
blocked by unavailable physical evidence.
