# G2 bootloader event-flags set `0x0041652E` source closure

The authenticated 94-byte body `[0x0041652E,0x0041658C)` hashes to
`46e258aaf8b560d3617e4570d332ac2d274eb0aa1f1a4b40d4dd2756ff0cf005`;
both direct callers are pinned.

`runtime_flags_set_41652e.c` preserves invalid object/mask rejection, task and
ISR backend selection, ISR result merging, and the conditional PendSV write to
`0xE000ED04`. Apple and Linux each emit an 84-byte leaf under four strict
relocations. Host and offline production/package gates pass. The interrupt,
PendSV, and scheduler effects require physical execution and are explicitly
blocked by unavailable authorized responsive G2 evidence.
