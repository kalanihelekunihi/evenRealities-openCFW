# G2 bootloader event-flags wait `0x00416590` source closure

The four bytes at `[0x0041658C,0x00416590)` are retained authenticated data
(`0x200270D4`). The following complete 128-byte wait wrapper hashes to
`df03eb8655d29e3f5b6a64d2dc42f56c716c83f56f6c6689afd419f7e824d6db`;
its caller at `0x0042E2C0` is pinned.

`runtime_flags_wait_416590.c` preserves object/mask validation, critical-
context timeout mapping, wait-all and clear-on-exit option decoding, retained
backend invocation, satisfaction testing, and timeout/error results. Both
profiles emit 100 bytes under two strict relocations. Offline gates pass;
live scheduler timing remains blocked by unavailable physical evidence.
