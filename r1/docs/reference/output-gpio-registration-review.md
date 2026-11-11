# R1 output-GPIO record and registration closure

The existing five-record output-GPIO provider now participates in relocatable
composition. Its source and compiled object are unchanged. Direct execution
of the locked stock scatter loader, stopped before runtime entry, recovers
all 340 bytes of the configuration. The source object reproduces those bytes
when test-only name/callback references are relocated to their observed native
addresses. This is a data comparison, not permission to add fixed executable
addresses to a qualified source build.

The five records are `ppg_led_en` on pin 10, `touch_ldo_en` on 30,
`ppg_reset_en` on 36, `ship_mode_en` on 9, and `touch_rdy_out` on 17. The
comparison includes every record field, initial zero, configuration byte,
driver callback and operation slot. It checks stock configuration; physical
wiring and electrical behavior remain untested.

REA observes the 42-byte registration body at `0x54E78..0x54EA1`, inclusive.
It walks five 56-byte records from `0x20007228`, copies each name into the
embedded device at +32, installs the operation table at `0x20007358`, and
registers each device in order. Assembly and execution show that the final
registry result remains in r0; the decompiler's inferred void signature does
not establish a source return type.

All 486 stock-versus-source execution comparisons pass. They cover all
five-call combinations of statuses 0, 7 and `0xffffffff`, both with and
without controlled mutations of future names and current opened bytes.
Checks include state visible before every registry call, complete final
configuration bytes, five-call ordering, return value, SP and r4–r6
preservation. Earlier failures do not abort registration, later record names
are loaded after prior calls, and the final registry status is returned.

All 561 R1 units compile and both payloads compose with no duplicate strong
symbols. The output configuration import resolves, reducing application
imports from 242 to 241; bootloader imports remain 34. No new imports, source
qualification entries or workflow gates were added. Callback metadata types,
live registry/device behavior, final firmware linking and whole-image byte
identity remain separate work.

[output-gpio-registration-review.json](output-gpio-registration-review.json)
binds scatter output, source/report hashes, the data comparison, REA evidence
and execution counts. Probes and the neutral snapshot remain under ignored
`build/goal-r1-output-gpio/`.
