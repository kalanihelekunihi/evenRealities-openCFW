# R1 EAT TX callback registry in C, 2026-11-10

`native_eat_tx_registry.c` reconstructs stock callback-slot registration
`0x3d7fc` and its two default registrations at `0x3d7ac`. The 36-byte
source-owned registry retains the stock mask at offset 16 and three callback
slots from offset 24. Channel one binds the channel-zero SEGGER RTT writer;
channel two binds the BLE type-two sender. Their C wrappers in
`native_console.c` and `native_tx.c` replace stock `0x3e00e` and `0x3dff8`.

The callback register's actual Clang object was linked in an ignored
Cortex-M4 probe at `build/r1-tx-callbacks-c-20261110/`. Four hundred paired
stock/C calls with randomized initial 36-byte state, channel and callback
word match all registry bytes. The two default callbacks follow the stock
disassembly's calls and argument mapping; full RTT/BLE hardware behavior is
not established by this probe.

`./make.sh sources-check` passes with 981 R1 units in 768 source files.
`build/sources-r1-eat-tx-registry-c-20261110/report.json` compiles and
composes all 899 application and 82 bootloader units with no duplicate strong
symbols. The strict bootloader link at
`build/r1-boot-link-eat-tx-registry-c-20261110/report.json` passes with a
valid 512-byte vector. The strict application attempt at
`build/r1-link-eat-tx-registry-c-20261110/report.json` still has 20 undefined
functions and reports 626,408 of 696,320 flash bytes used. The new registry
is not yet reachable because EAT core initialization and command dispatch
remain unimplemented; it does not close a final-link import by itself.

The stock EAT command table has 37 entries, each 16 bytes, at
`0xc419c..0xc43ec`. Its callback functions still require source ownership
before a faithful C core initializer and dispatcher can bind the table.
