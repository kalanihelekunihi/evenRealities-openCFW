# R1 source-build repairs

The consolidated manifest's ten expected compile failures were repaired on
2026-10-21. A complete R1 source build now compiles all 487 application and
74 bootloader units, with no expected failures or duplicate strong symbols.
The manifest now also composes the 449 participating application objects and
74 bootloader objects with GNU `ld -r`. Both succeed, with 238 unresolved
application imports and 34 bootloader imports. The
[i2c_5 callback repair](twi-delay-review.md),
[GPIO closure](twi-gpio-review.md) and
[LIS transport closure](lis-transport-closure.md) and
[hardware-TWI registration](hw-twi-registration-review.md) and
[output-GPIO registration](output-gpio-registration-review.md) document the changes from the
initial 560-unit, 253-import application baseline. These are measured composed
results; no aliases or warning-suppression flags were added. Compilation and
relocatable composition do not establish final firmware linking or byte identity.

A later isolated diagnostic composition linked 436 participating application
units and all 74 bootloader units with GNU ld `-r`. Both commands succeeded,
but the application emitted mixed enum-size ABI warnings. This is not proof
that cross-TU structures agree. Those initial diagnostic result/log paths are retained under
`build/goal-r1-composition/report.json`. The FlashDB layout mismatch was
subsequently repaired as described in [the ABI review](flashdb-abi-review.md).
The remaining mixed-enum interfaces still need individual review.
The normal build now repeats that diagnostic automatically; see
[the composition review](source-composition-review.md) for the current report
and import-provider evidence.

## Restored SDK build context

The power-management, RTC-driver, SoftDevice observer, SoC observer,
fstorage FIFO configuration, DFU-state and software-TWI GPIO units had
incorrectly used a freestanding profile without Nordic SDK includes. They
now use the existing strict Nordic application profile
`r1-application-14`, with the pinned nRF5 SDK 17.1.0, existing recovered SDK
configuration and `-Wall -Wextra -Werror`. The selected log formatter uses
that same profile. No oscillator, LF-clock, interrupt-priority, GPIO or
peripheral configuration value was changed.

The RTC bridge now declares its callback as `nrfx_rtc_handler_t`, and the
tick callback takes `nrfx_rtc_int_type_t`. This removes the incompatible
function-pointer cast while retaining the callback's ignored event argument
and existing tick behavior. The lifecycle translation unit uses the same
SDK profile. Existing instance/configuration size and offset assertions
continue to pass.

## FlashDB layout

`native_flashdb_tsdb_kernels.c` uses the existing FlashDB configuration and
include profile with inherited `-fshort-enums` and strict warnings. Both
upstream FlashDB compiler profiles now specify that ABI explicitly. Without short
enums, the vendor `tsdb_sec_info` grows and `fdb_tsdb` is 108 bytes, violating
the existing 100-byte native extent and field-offset assertions. The fixed
build passes every existing extent/offset assertion, including the sector
status at offset 1 and the 40-byte sector record. No assertion was relaxed,
and no FlashDB vendor header or storage policy changed.

The complete ABI review verified the native field operations, both compiler
layouts, unchanged serialized geometry and 52 valid control cases per
compiler. That supersedes the earlier kernel-only flag fix, which left the
Clang-compiled upstream provider on the wrong layout.

## Selected translation-unit cleanup

The selected calendar TU contained an unused forward-converter buffer and
month table, and an unused cache helper copied from the full family. These
were removed; the inverse table and three selected converter/adapter bodies
remain. The original family implementation is unchanged.

The selected Nordic log formatter delegates prefix handling to
`r1_log_prefix_process`; its unused severity table and private timestamp
helper were removed. Timestamp frequency/divisor state and initialization
remain. The DFU-state callback explicitly ignores its unused context. No
warning was disabled to make these source files compile.

A focused comparison compiled the original five edited C translation units
under the repaired build context, allowing only their old diagnostics in the
isolated probe. Every allocated ELF section and normalized relocation was
identical to the strict repaired build. This checks that the cleanup and RTC
type repair do not change generated code/data under this Clang profile;
it is not comparison against the original firmware compiler. Probe and
results: `build/goal-hardware-r1/compare_repairs.py` and
`build/goal-hardware-r1/old-sources/comparison.json`.

At the compile-repair stage these candidates retained `link: false`.
Subsequent bounded reviews, including [RTC lifecycle](rtc-lifecycle-review.md),
include checked providers in relocatable composition. Neither step admits them
to a qualified source plan or establishes source completeness. Experiments
and the full R1 report are under `build/goal-hardware-r1/` and
`build/sources-goal-r1-hardware/report.json`. The tracked summary in
`g2/evidence/source-build-goal-validation.json` binds the final validation
reports and manifest identities. Hardware behavior and original-compiler
code generation remain separate verification steps.
