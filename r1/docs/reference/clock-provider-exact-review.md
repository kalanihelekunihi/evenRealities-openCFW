# Exact RTC request and backend providers

The wrapper frame contract below is superseded by the [ordinary C backend wrappers](clock-port-pure-c-review.md). Their two exact selections have been retired; the callback-binding request selection remains.

Three RTC fragments from `r1/src/application/board/native_clock_port.c` now enter the canonical source plan through official qualification: `r1_clock_backend_bind_tick` at `0x50daa` (12 bytes), `r1_clock_backend_update` at `0x50db6` (10 bytes), and `r1_clock_rtc_bind` at `0x50de0` (12 instruction bytes plus a four-byte literal). These contribute **38 new exact bytes**. Existing selections remain unchanged.

The request functions are now explicitly out of line. Previously Clang inlined their bodies into the backend wrappers, removing the native call boundary. Empty fixed-R4 compiler constraints retain the native R4/LR wrapper frame without emitting instructions. The wrappers now match stock's calls and unconditional return value 1, including the callback move from incoming R3 to R0. This is compiler-specific C rather than portable ISO C.

Official generic qualification admits both wrappers under the recorded profile and the callback-binding request under `-Oz`; the resulting source plan retains those compiler arguments and native relocation bindings. The complete bind request includes its cached-device literal, not just the instruction prefix. GCC9 qualification independently accepts the two wrappers; its rediscovery of the already admitted charger thunk is not counted as new coverage. No pinned upstream source or normal manifest flags changed.

REA read the 70-byte stock window from `0x50daa` through `0x50def`, covering the wrappers and bind request as well as the intervening helper. Qualification compares complete linked bytes at their independently named native entries. Only the three qualified regions enter the source plan; the intervening helper is not admitted by that byte read.

The normal compiler object passes **256 paired wrapper cases / 512 executions** against stock. The fixture models the request providers, varies full-width arguments and return statuses, checks native SP minus 8 and active R4-R11 at provider entry, and compares all R0-R12 values and APSR on return, final SP and interrupt masks. The wrappers return 1 regardless of the provider's status. LR return-address bits and physical hardware are excluded. The callback-binding request itself is established by full linked-byte equality including its literal.

All 576 R1 units compile and compose without new failures or duplicate strong symbols. All 575 other objects and the other three clock functions' bytes and relocations remain unchanged. Imports remain 164 application / 34 bootloader. Existing source-plan units are unchanged; two qualifier-generated units add three regions.

The canonical hybrid application still matches locked SHA-256 `0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a`. Ownership is now **3,999 source-built bytes**, 642,161 fallback bytes and 248 resource bytes. Source-built totals include assembly and data. Native-address bindings for RTC storage and request/registry providers do not establish a complete final source link. Source completeness remains false; electrical behavior and physical operation are unverified.

Battery recovery was also reviewed. Its saved R1/R2/R3 words at SP minus 40 double as outgoing ring/SDK log arguments, and timestamp pointers can alias that storage. A direct C replacement must preserve that overlap. The existing battery wrapper was retained; this review does not weaken its evidence boundary or claim it has been converted.

Evidence: [clock-provider-exact-review.json](clock-provider-exact-review.json). Qualification, wrapper execution, source-plan backup and audit probes are under ignored `build/goal-r1-hardware-provider-qualification/`. Normal report: `build/sources-goal-r1-clock-provider-exact/report.json`; hybrid report: `build/hybrid-goal-r1-clock-provider-exact/build-report.json`.
