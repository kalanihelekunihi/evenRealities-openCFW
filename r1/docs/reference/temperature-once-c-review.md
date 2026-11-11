# R1 temperature one-shot measurement control in C

`native_temperature_once.c` supplies stock entry `0x4b6c0` and its existing event-service alias. The normal Clang build resolves the unchanged assembly event adapter at `0x42514` to this C implementation.

Any nonzero direct argument enables measurement. An existing once handle suppresses duplicate registration. Otherwise the implementation clears the shared fourteen-byte temperature record, sets byte 12 to 1, registers stream `temp` with consumer `once`, sample callback `0x4b921` and both options equal to 1, then stores the returned handle. A zero argument unregisters an existing handle before clearing its cell. The outer adapter retains its length gate, boolean normalization and logging.

This reuses the existing canonical handles at `0x2001e3cc` and record at `0x2001e3dc`. There is no new state owner. The stock offset is deliberately preserved: one-shot and periodic measurement use the same record.

Verification compared 700 stock/C cases: direct and actual adapter calls, raw nonzero arguments, lengths, existing and failed registration handles, logging modes, provider mutations and repeated enable/disable sequences. It checks provider order and arguments, guarded state, preserved registers, stack pointer and interrupt masks. Eight compiled defects were rejected: low-byte enable truncation, wrong handle slot, missing duplicate gate, wrong clear length, wrong flag byte, wrong stream consumer, early handle clear and missing handle clear. The normal implementation passed again afterward.

REA returned the complete 62-byte function, verified against the official raw artifact. See [REA evidence](temperature-once-c-rea.json) and [structured verification](temperature-once-c-review.json).

All 760 R1 units compile with no duplicate strong symbols and both payloads compose. All 759 previous object hashes are unchanged. Application imports decrease from 129 to 128; bootloader imports remain 34. R1 source coverage passes (564 source files, none unaccounted). The global source check retains the existing G2 `resident_rom_thumb_set.S` manifest omission.

Stream registration, teardown, memory clearing and logs are modeled providers. Callback identity is checked; asynchronous scheduling and physical temperature data are not tested. Private scratch, caller-clobbered registers and the void return are excluded. Relocatable composition does not prove complete firmware linking or device operation. Byte identity is not required for this build route.
