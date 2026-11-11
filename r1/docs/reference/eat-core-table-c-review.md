# R1 EAT command table and core initializer in C, 2026-11-11

`r1/src/application/runtime/native_eat_command_table.c` supplies the
37-entry source-owned EAT command table. A bounded check of the locked stock
`0xc419c..0xc43ec` table confirms every flag, name, callback identity, and
entry position. Callback symbols are explicit C dependencies; the table
contains no stock executable bytes.

`r1_eat_core_init` in `native_eat_tx_registry.c` installs that table and its
count, registers RTT/BLE TX callbacks, clears the reserved word, enables the
first two registry flags, and logs the command count. The ignored probe at
`build/r1-eat-core-init-20261111/compare.py` compared 400 paired stock/C
initializations with randomized prior registry bytes and log modes. Registry
state and log arguments matched after normalizing source versus stock
addresses. The tested registry object is byte-identical to the manifest
object, SHA-256
`61b2beeb6890ab27ca72e7c16f1064c8a655561f3245337bb24638f16b7ebdf8`.

`r1/src/application/runtime/native_eat_slow_command.c` supplies the
`AT^BSLOW` callback at stock `0x4ee72`; 400 paired stock/C cases matched its
connection lookup and immediate slow-mode call. The manifest retains the
pinned SDK `SEGGER_RTT_Write` implementation now reached through the TX
default. The startup and callback probes model lower providers and do not
validate RTT transport, scheduler execution, or physical BLE behavior.

`./make.sh sources-check` passes with 987 R1 units, 774 source files, and no
unbuilt R1 units. The source build compiles and composes 905 application and
82 bootloader units with no duplicate strong symbols. The strict bootloader
link and C vector pass. The strict application link uses 630,360 of 696,320
flash bytes without overflow, but has 50 undefined references: 36 EAT table
callbacks and 14 other application functions. This higher count exposes the
command table's real dependencies after making it reachable; it is not a
link regression masked by placeholders. Receipts:

- `build/sources-r1-eat-core-slow-c-20261111/report.json`
- `build/r1-link-eat-core-slow-c-20261111/report.json`
- `build/r1-boot-link-eat-core-slow-c-20261111/report.json`

The 36 callbacks, the other imports, embedded assembly, whole-image byte
equality, and hardware execution remain unfinished.
