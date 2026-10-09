# Clock timing, IRQ and poll source closure

Five reconstructed helpers pass **1,598 direct comparisons**:IRQ save/mask,ITCM spin,delay,status-change wait and equality/inverted-equality wait. Final combined ELF also passes **21,437 reused numerical/ownership/composition cases**:13,920 math,2,530 generator,1,584 public dispatch,1,144 config,1,407 driver,816 manager,36 stock request/release. Total23,035 describes one artifact; it is not distinct global coverage. ELF SHA256 `4f75c392ee947f969c7f8f9cedd56f9da03c61b02fb566a14c86797bdb481fed`. [Readable source](../../components/audio/clock_timing_offline/timing.c), [interface](../../components/audio/clock_timing_offline/timing.h), [pseudocode](pseudocode.md), [exact validation](exact-build-validation.json), [addresses/hashes](function-bindings.json).

## No original executable provider in the tested source chain

All native clock manager/driver,oscillator,generator,float-runtime,IRQ,delay and poll providers now link to source implementations. The final linker has **zero original-code aliases and zero unresolved symbols**. More strongly, a code hook in every native execution across all eight suites aborts ifPC leaves0x100000..0x110000; all23,035 source cases pass. Original guests execute authenticated stock bytes independently. This proves the reached executable closure under these fixtures, **not a full native firmware build**. The machine still receives authenticated startup/calibration/scalar data and synthetic MMIO; no whole-image byte equality or live hardware readiness is inferred.

## Delay arithmetic and actual ITCM provenance

IRQ helper0x473940 returns savedPRIMASK and disables interrupts; callers restore that saved value. Native source preserves both masks tested. Delay0x4807A0 converts uint32microseconds tofloat,then unsigned fixed-point with5 fractional bits (nominal*32). It reads0x40021000 bits3..4. Value2 converts this count throughfloat*250/96 and subtracts overhead24; other values subtract15. It enters spin only when count>overhead. Native source preserves all floating conversion/rounding/saturation/FPSCR effects under the explicit scalar profile, not a host estimate.

The original spin is **0x40..0x46 from the authenticated startupITCM record**, not an assumed residentROM body. It decrements then branches while nonzero. Native source expresses the loop, without a retained opcode array. Standalone count0 would underflow and require2^32 iterations; it is excluded from completed-spin fixtures. The caller proves a positive argument through its overhead guard.

Huge delay inputs stop at actual spin entry and compare count/FPSCR, without manufacturing completion. Completed small-delay/spin cases and large-input entry-cut cases are distinguished inresults.json. Source/API names establish microsecond units, but original/native instruction execution does not prove physical elapsed time onM55,cache/clock/interrupt effects or scheduling behavior.

## Poll-before-delay and boundary semantics

Status-change0x4807FC andstatus-check0x480826 load the register and compare `(word&mask)` to the **unmasked expected word** first. Check uses byte-narrowed fifth argument:nonzero waits for equality;zero waits for inequality. Values256→0 therefore invert the condition. Public wrappers should validate boolean/input domains.

Budget0 still reads status once and returns0 if matched,otherwise4 with no delay. A mismatching poll with remaining budget callsdelay(1),then polls again; the final permitted delay can be followed by success even with budget now0. Persistent mismatch performs budget+1reads and budget delays before returning4. There is no readiness latch or atomic hardware transition guarantee. Tests change status at explicitly selected reads; these transitions are synthetic,not realIRQ/device observations.

The original/native comparison includes read sequence,delay/spin counts,return,fullFPSCR,PRIMASK andrestoredSP. Driver/manager sequencing still reproduces force-bit timeout followed by cached success and lateSYSPLL lock failure with retained ownership. Return success,software commands and actual readiness remain distinct.

## Numerical/error invariants and validation corrections

Full float-runtime andSYSPLL suites are rerun on this exact final artifact. NaN/domain/errno behavior and min-VCO partial writes remain unchanged; no supported API is inferred from malformed configurations. Under checked fixtures the source guest never reaches any original math or error helper.

The timing trace was strengthened to track active spin calls rather than deduplicating identicaladdress/LR pairs. A copied driver trace map initially missed nativewait5; it was extended and all1,407 cases rerun on the unchanged ELF. Inherited provider-limit descriptions were corrected as documentation only. Exact validation records these corrections and the executable guard.

## Remaining source leads and boundaries

This bounded clock dependency chain has no remaining original executable bindings. [Remaining-source ledger](source-lead-ledger.json) retains broader actionable leads:actualFreeRTOS timer-daemon command/expiry/tick handling,touch callback/reentrantI2C ownership and selected STM32 case peripheral adapters. Dirty file-close/media behavior needs mounted block/cache inputs. Runtime vendor/version attribution remains open even though the four bounded math algorithms are reconstructed; no pristine upstream source identity is claimed.

Real scheduler/device traces are still needed for physical shutdown/concurrency conclusions. The source guest/calibration/MMIO setup is an offline evidence model,not a source-complete boot image. No global source-exhaustion,whole-system shutdown safety or hardware patch recommendation is asserted.

All prior seals,110 inputs,four checkpoints and current staging are preserved. Only new owned analysis/component directories were written. No commits, production edits, shared state/gates or device writes. [Preservation](preservation.json).
