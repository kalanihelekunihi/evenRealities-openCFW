# G2 bootloader small runtime-services source closure

Five bounded services are now source-owned MIT C: critical state update at
`0x0042CEA4`, chunked indirect traversal at `0x0042D9F0`, hardware-channel
normalization at `0x0042EDA0`, platform boot sequencing at `0x004301D6`, and
address/length validation at `0x00430A60`. The `0x0042CEA4` boundary was
corrected through `0x0042CED8` so its complete PRIMASK restore and return are
classified as executable.

Apple clang 21 and Homebrew clang 22 reproduce all 274 authenticated bytes
exactly from mnemonic-only Arm source. Portable tests cover deferred versus
immediate state adjustment, chunk iteration, handle/control normalization,
clock-provider invocation, and validation bounds. Live register, clock,
interrupt-mask, platform-startup, and cold-boot behavior is blocked by
unavailable physical evidence.
