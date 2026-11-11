# R1 GoMore sleep statistics in C, 2026-11-10

`native_gomore_interval_statistics.c` implements stock `0x68fd4`, producing
seven float statistics. `native_gomore_stage_statistics.c` implements stock
`0x69128`, producing twelve. Each adapter passes the caller's stage pointer,
start/end timestamps and packed flag to the consolidated C primitives. The
stock modulo reader indexes a 2,880-epoch ring, so the source bindings use
2,880 unpacked bytes or 720 packed bytes.

The ignored probes under `build/r1-gomore-interval-stats-probe-20261110/`
and `build/r1-gomore-stage-stats-probe-20261110/` link the actual source
objects and compare them with the locked application in Unicorn. Both pass
**411 paired cases** with exact output bytes and unchanged guard bytes. The
cases include empty and sub-epoch intervals, 30-second boundaries, packed
flags 1 and 3, unpacked input, deterministic stage patterns, and ring wrap.
The earlier score-flow review verifies the caller's forwarding and 28-byte
offset to the second output; the two direct probes establish the newly bound
providers. Long intervals near the 2,880-epoch cap, invalid pointers and
physical sleep data are outside these probes.

All 962 R1 source units compile without failures or duplicate strong
symbols. The strict bootloader link passes. The application now has 40
undefined references and exceeds its full flash load region by 29,864 bytes.
These two adapters add 48 bytes each to the flash load.
