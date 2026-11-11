# R1 dormant estimator stage in C, 2026-11-10

Stock application `0x5feb8` stores its state pointer, checks the dormant
estimator mode, composes a per-sample record, and replays that record in mode
one through stock `0x96e0c` and `0x721b4`. The native C entry is
`r1/src/application/runtime/native_gomore_dormant_estimator.c`; it calls the
consolidated `gomore_primitives_dormant_estimator_update` implementation.
The record-step callback at `0x721b4` is now bound to
`r1/src/application/runtime/native_gomore_dormant_record_step.c`. The record's
last word is a float input; stock passes the estimator state to the heart-rate
ratio wrapper. Its running moments start at estimator offset `0x210`, while
the profile flag is at offset `0x0d`.

The locked stock function writes a pointer cell at `0x20007ce8`. In the
current source link map, `0x20007cdc` through `0x20007d03` belongs to the IQS
model table, so writing the literal stock cell would corrupt that table. The
C entry stores the pointer in the source-owned
`r1_gomore_dormant_active_state` symbol. Future users of this binding must
reference the symbol, and the source link must verify its RAM placement.
The current linker map places it at `0x20024c84`, clear of the IQS table.

The ignored Cortex-M4 comparison under
`build/r1-dormant-stage-adapter-20261110/` executes the stock entry and the
C adapter with the same inputs. For 144 mode-zero, mode-two, and mode-three
cases, return value, all 828 state bytes, 68 output bytes, and the pointer
binding agree. A separate replay using the actual manifest Clang objects and
source-owned math objects exercised both stock and C callbacks on 288 mode-one
cases. The callback was entered once per run on both sides. All 288 cases
agree in return value and the compared state, output, pointer binding, and
auxiliary buffer. The cases include high-speed paths through cubic root
selection, zero and boundary heart-rate values, and six flag configurations.
The earlier 48-case mode-one replay was invalid because its sequence counter
rejected every record. The 288-case replay corrects that setup. Broader input
and state coverage, application boot, and physical sensors remain unverified.

The current source build has 978/978 compiled units and no duplicate strong
symbols. The strict bootloader link passes; the strict application link has 22
unresolved functions and uses 615,432 of 696,320 flash bytes. Its receipts are
under `build/sources-r1-dormant-roots-c-20261110/`. Board boot and physical
sensors remain unverified.
