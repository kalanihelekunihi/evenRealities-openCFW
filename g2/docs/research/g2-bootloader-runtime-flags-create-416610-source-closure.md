# G2 bootloader event-flags create `0x00416610` source closure

The complete 154-byte body `[0x00416610,0x004166AA)` hashes to
`b41ac55ec65b009015e3839d778bf3b9ea73e9280457e348428591bb7ccea77d`;
all six direct callers are authenticated.

`runtime_flags_create_416610.c` preserves the critical-context guard,
attribute-bit rejection, tagged kind selection, exact dynamic or at-least
80-byte static-storage contract, retained constructors at `0x00419DA8` and
`0x00419DC2`, and nonnull result tagging. Each compiler emits 82 bytes under
three strict relocations. Eight host tests and all offline production gates
pass; live object lifetime remains blocked by unavailable physical evidence.
