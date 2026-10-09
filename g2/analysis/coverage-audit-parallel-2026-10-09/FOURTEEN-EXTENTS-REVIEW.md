# Fourteen additional extents independently reviewed

All14selected candidates pass, totaling544new comparator bytes. [Verification](FOURTEEN-EXTENTS-VERIFICATION.json), [parser](fourteen_verify.py). No builds or original instructions were executed.

| Receipt directory (under g2/analysis) | Selected additions | New bytes |
|---|---:|---:|
| touch-sysint14-linkage-2026-10-09 | SetVector, Init |124|
| touch-syslib14-assembly-2026-10-09 | DelayCycles, EnterCriticalSection, ExitCriticalSection |32|
| touch-syslib14-delay-linkage-2026-10-09 | Delay, DelayUs |72|
| touch-systick14-linkage-2026-10-09 | ServiceCallbacks, Init, SetCallback |156|
| touch-pdl14-inline-emission-2026-10-09 | SetRxFifoLevel |44|
| touch-clkhf14-attribution-2026-10-09 | ExtClkGetFrequency, GetSource, SetSource at historical divider rows |116|

Every linked section's full bytes, hash, length and address match the locked target, including dependencies. Input objects match receipts previously independently reviewed against authentic source/dependency hashes. Linked output and linker-script hashes verify; script copies agree. The actual GNU compiler hash matches the prior audit and linker hash matches its receipt. Assembly source and object hashes verify; source-label offsets0/18/26 agree with the three predeclared extents, even though ELF declared sizes are zero. The32-byte assembly contains no relocations. T412/Cortex-M0+/Thumb/-Og remain the explicit assembly/inline compile configuration. The emission unit adds only typed data pointers taking authentic header function addresses; it does not implement a substitute wrapper. Inline header hashes verify.

Source-object and linked-section comparison shows no changes outside relocation words. Each ARM ABS32 binding independently checks the symbol address plus original word addend; each Thumb BL independently decodes to the authenticated target function. Recorded original PC-relative LDR references independently bind RAM vectors0x20000400, ROM vectors0x3300, delay globals0x2000086C/870/874, callbacks0x20000F40, and external clock word0x20000F20. SysTick unnamed section-symbol relocations bind the real .bss section rather than invented unnamed functions. Every four-byte literal-pool word in linked full spans is referenced by original instructions; ELF mapping boundaries agree. New extents overlap neither each other nor any other selected historical instruction span. NOLOAD callback/global bindings supply addresses, not initial values or fabricated runtime providers.

The two divider alternatives are concrete rejected comparisons: their emitted bytes/hash and mismatch positions independently verify. Unchanged source-selection bodies match0x9F34/0x9F44 exactly; therefore the historical GetDivider/SetDivider names are incorrect at those addresses. Corrected semantic attribution resolves those two existing rows, without expanding the54-entry denominator. The independently selected historical SetSource row at0xA188 remains present and unresolved; it must not be merged into0x9F44.

Accounting after prior reviewed2368bytes/25functions: +544bytes/14functions =2912bytes/39selected functions.54selected=39reviewed+15remaining, all15remaining are relocation/extent boundaries. The three assembly absences, two historical divider absences and one inline-emission boundary are now resolved. The96-byte NVIC helper is validated dependency evidence outside the selected denominator and excluded from2912. The reused32-byte assembly and48-byte SysTick enable/clock extents are also excluded from increments. Do not present2912as instruction-only bytes or whole-firmware coverage; extents include owned literal/alignment bytes. Exact source comparators establish neither physical delay calibration, active vector contents, callback execution, interrupt delivery, original TU/toolchain uniqueness, nor bundle completeness.

All output stays in the assigned audit directory. Canonical ledger updates remain the owner's responsibility; sealed failures and historical symbols were not changed.
