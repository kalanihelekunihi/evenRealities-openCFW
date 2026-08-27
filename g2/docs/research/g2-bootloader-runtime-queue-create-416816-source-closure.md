# G2 bootloader message-queue create `0x00416816` source closure

The complete 140-byte body `[0x00416816,0x004168A2)` hashes to
`0529769ef0cd634c8a643a7c412f804d9c530fcc2e5b54a87b532b8ec3fb583a`;
both direct callers at `0x0042DD7C` and `0x0042E550` are authenticated.

`runtime_queue_create_416816.c` preserves critical/zero-argument guards, the
exact dynamic-empty configuration, the 80-byte control-storage threshold,
message-buffer capacity check, and retained static/dynamic queue constructor
argument order. Apple and Linux each emit 100 bytes under three strict
relocations. Five host tests, both target profiles, provider/manifest routing,
and both unsigned packages pass offline. Live queue/scheduler behavior is
blocked by unavailable authorized responsive G2 physical evidence.
