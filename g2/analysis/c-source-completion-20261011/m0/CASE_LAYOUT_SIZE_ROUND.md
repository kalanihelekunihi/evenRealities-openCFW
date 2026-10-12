# CASE source-only reset and size experiment

The authenticated official `firmware_box.bin` is 55,784 bytes including its
32-byte package header, so the stock Cortex-M payload is 55,752 bytes. These
links are diagnostic C outputs. They are not CASE replacement images.

| Source/link profile | PT_LOAD bytes | Over stock payload | Undefined imports |
| --- | ---: | ---: | ---: |
| Selected `-Os` command/startup, no GC | 65,308 | +9,556 | 0 |
| Selected `-Os`, section GC plus two native event callback roots | 60,012 | +4,260 | 0 |
| Selected `-Os` command, mixed `-Oz` startup | 58,000 | +2,248 | 0 |
| Isolated `-Oz` rebuild of all 153 selected command units, mixed startup | 57,248 | +1,496 | 0 |
| Same with all 39 aligned native pointer leads retained | 57,272 | +1,520 | 0 |
| Pre-sensor-root profile with `-fmerge-all-constants` on command units | 57,232 | +1,480 | 0 |

The admitted selected archive is unchanged. The startup size variant retains
`application_policy_idle_candidate.c` and
`application_policy_no_reply_candidate.c` at `-Os`: at `-Oz` their constant
modulo expressions introduce `__aeabi_uidivmod` without a source provider.
The 28-byte local difference does not justify inventing that provider. The
all-constants merge profile is diagnostic because string/constant pointer
identity has not been checked against the native program.

`case_reset_placement_probe.ld` fixes the 46-word vector at `0x08000000`
and reset code at `0x08000144`. The mixed GC ELF has entry `0x08000145` and
its first two vector words match stock (stack `0x20002c88`, Thumb reset
`0x08000145`). Other source functions are relocated and the full vector table
does not match stock addresses. The latest `-Oz` command probe ELF SHA-256 is
`bf95e51bfe57003d53d29b67a29bab94d546b22cca40504b44ca4b7f48a2e8f0`.

The existing native pointer census finds 39 aligned candidate Thumb targets,
15 outside both the fixed catalogue and direct BL targets. The vector-root
GC initially omitted two genuine event callback entries and the sensor
cancel callback at native `0x080086e0`. The two event callbacks are explicit
linker roots. The sensor IRQ C body now stores the relocated typed
`case_boot_sensor_cancel_callback` function address rather than a stock
absolute executable address; this automatically roots that callback.
`verify_case_sensor_irq_callback_relocation.py` checks the native/C pointer
store with source-address normalization and the existing IRQ oracle still
passes 512 bounded cases. `audit_case_indirect_link_roots.py` confirms all
39 known aligned pointer source symbols appear in the 57,272-byte ELF.
This is a bounded presence check. Runtime-constructed callbacks, external
peripheral entry, and stock whole-program indirect reachability remain open.

The measured remaining size deficit is **at least 1,520 bytes** for the
currently retained source graph; additional required roots or product data
can increase it. No larger flash region, source-owned secondary placement,
or package-length change has been authenticated. The experimental linker
discards unwind tables and is not a complete flash/scatter script. Required
next evidence is a rooted source reachability map (including callbacks
formed at runtime), followed by a qualified placement/capacity contract.
Formatter invalid pointer, unbounded width/precision, and callback-fault
domains remain separate runtime-equality gates.

## Semantic text and corrected callsites

The earlier size figures omitted stock string data referenced by absolute
addresses in reconstructed C. The selected Case graph now includes a
`semantic_strings_candidate_20261011` C catalog with 203 distinct named
NUL-terminated objects, 6,466 semantic source bytes. The generator pins the
official package SHA and records each native address, length, and byte hash.
The C callsites use relocatable symbols; the sole remaining `0x0800xxxxu`
constant in selected C is the flash-option bitmask `0x08000000u`.

Native Thumb ADR and PC-relative literal loads qualify 16 corrected logger
format/message bindings in the two transport workers and record dispatch.
`verify_case_logger_literal_bindings.py` checks the exact instruction-to-text
address pairs; `verify_case_semantic_strings.py` verifies compiled C bytes.
This does not qualify every logger callsite or malformed format domain.

The latest isolated optimized/GC source layout after these corrections has
PT_LOAD `0x0f970` = **63,856 bytes**, 8,104 above the stock payload, with
39/39 retained native aligned pointer leads and zero unresolved imports.
The ordinary `-Os` absolute experiment before pruning two unused interior
substrings loaded 71,776 bytes. The optimized ELF SHA-256 is
`c5028fead1bc5c6339f8a2df65ac9818468d09333c85dfe8e9211d4967b14fdf`.
These are diagnostic source links with provisional roots and no authenticated
flash-capacity contract; neither is a replacement firmware image.
