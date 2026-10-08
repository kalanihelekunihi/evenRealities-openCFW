# Complete bounded PCM2.2 table recovery and source comparison — 2026-10-08

**All27 registered PCM2.2 transition-table entries now have readable reconstructed bodies and bounded original-instruction comparisons.** This batch adds32 exported functions:23 previously opaque nontrivial table bodies,3 no-op table bodies,2 cache providers, the TON provider and3 registered/vector wrappers. It links the7 sealed transition/timer functions from the prior batch, including table entry2 and delayed completions. This is39 selected native functions in the test ELF, not complete source-built firmware, independent whole-corpus review or byte equality.

The exact final ELF `32f579076bf8ecd051b76377d6678dbd1d92bc0faebd4f41cd7706df65d8b53c` passes **12,019 comparisons**:10,655 new-family/provider/wrapper/composition cases and1,364 linked prior-function regressions. [Exact-build linkage](exact-build-validation.json), [reproduction build](build_offline.py), [complete family interface](../../components/audio/transition_producers_offline/producers.h), [readable C reconstruction](../../components/audio/transition_producers_offline/producers.c), [original disassembly](disassembly-evidence.txt), [per-body original addresses/hashes/providers](table-bindings.json). A final header-only include rebuild produced the same ELF hash; no extra test execution is claimed for that declaration-only change.

## What the family does

All active bodies first read selected calibration fields, optionally finish a preceding timer operation, and publish target/trim globals. They then differ in TON setting, rail-trim boosts, coreLDO updates, CPU low/high requests, power-domain selector changes, cache handling, and delayed completion. Bodies are tested directly with explicit synthetic input state; this does not imply every artificial input pair is naturally selected by stock routing.

|Index|Original entry|Direct comparisons in this ELF|Newly explained behavior|
|---|---|---:|---|
|0|0x5a1f04|440|Normal VDDF boost50us, cached selector switch20us, final core/VDDC; matching-active-timer cancellation bypasses publish/normal completion|
|1|0x5a20e8|368|VDDF/VDDC boosts50us, core settle5us, cached CPU/AOR selector switch20us|
|2|0x5a22c0|1024|Previous sealed producer: delayed boost50us, pending2|
|3|0x5a2462|336|TON, VDDF double boost50us, restore|
|4|0x5a2586|336|Load core/VDDC/VDDF, TON, clear AOR/CPU/stat-selector bits|
|5|0x5a26be|360|TON, unconditional LP request/domain switches/HP attempt, then core/VDDC|
|6|0x5a28c0|336|Restore VDDF then TON|
|7|0x5a29a0|1704|TON, unsignedfloat0.9 VDDF margin, VDDC boost, timer50us, pending7|
|8|0x5a2c30|336|Publish and TON only|
|9|0x5a2d24|336|Restore VDDF then TON|
|10|0x5a2e10|336|Publish and TON only|
|11|0x5a2eea|360|Unconditional LP/domain/HP attempt, core/VDDC then VDDF boost50us, TON|
|12|0x5a3122|336|VDDF boost, core update, wait50us, VDDF restore; no TON|
|13|0x5a326c|375|TON, unsignedfloat0.9 VDDF margin/VDDC boost50us, core settle5us, VDDF restore, LP/domain/HP attempt|
|14|0x5a34ca|336|Restore VDDF; no TON|
|15|0x5a35a4|384|Set low-voltage trim, core and VDDC; no TON|
|16|0x5a36ac|384|Set low-voltage trim only|
|17|0x5a3798|384|Boost low-voltage trim, core update, immediate trim restore; no50us delay|
|18|0x5a38ce|336|Boost low-voltage and unsigned2×profile0_VDDF-new_VDDF, VDDC50us/core5us, restore trims; no TON|
|19|0x5a3ab0|384|Boost low-voltage trim50us then restore|
|20|0x5a3bcc|336|Core update and5us settle; no TON|
|21|0x5a3cc6|1012|Set continuation flag; VDDF boost50us, cached domain switch20us; deferred21b finishes core/VDDC|
|22|0x5a3e80|336|VDDC boost50us, core5us, clear selector bits, VDDF restore then TON|
|23|0x5a3fe8|336|Publish and TON only|
|24|0x5a40b0|12|No-op BX LR|
|25|0x5a40b2|12|No-op BX LR|
|26|0x5a40b4|12|No-op BX LR|

Entry2's1,024 cases belong to the linked1,364-case prior-function regression receipt; other table rows belong to the10,655-case new receipt. Three12-case no-op tests compare state/writes, without turning a scratch return register into an API status contract. These numbers measure bounded test fixtures, not firmware coverage percentages.

## Stock-versus-public-source differences

The pinned SDK is a source lead, not an exact substitute. Stock7 and13 compute:

```c
uint32_t difference = new_VDDF - profile1_VDDF; // Unsigned subtraction.
uint32_t margin = (uint32_t)((float)difference * 0.9f);
uint32_t boost = new_VDDF + margin;
VDDF = boost >= 128 ? 127 : boost;
```

The original float datum is `0x3F666666` at5A2D0C/5A359C. With a lower new trim, the unsigned difference wraps and the resulting bounded tested boost clamps to127. This is instruction-proven arithmetic under synthetic calibration fixtures, not evidence that authentic device trims take this branch or that hardware has a defect. The public SDK uses an integer trim expression and an extra10us delay before VDDC boost that these stock bodies lack. Stock18 uses the unsigned expression `2*profile0_VDDF-new_VDDF`, with clamp; the public source uses another profile/sequence expression.

Stock completions2b/7b and several core-settle steps use5us where public code specifies10us. Stock12/14/15/18 omit public TON adjustment calls. Stock17 performs no public50us settle call. Stock11 includes a VDDF boost/50us restore not present in public11. Original call lists and ordered MMIO comparison records preserve these differences. Intended microsecond units are corroborated by HAL; physical clock/timing is unmeasured.

Stock0/1/21 ignore cache-disable/enable error returns and continue their power-register sequence, whereas public macros return early on failure. New independent cache functions match the actual stock guard atE001E300 bits8..9 and the SCB CCR/ICIALLU plus DSB/ISB sequence.24 enable and24 disable fixtures cover enabled/disabled/mixed CCR, both PRIMASK values, and cache-power states0/100/200/300. Passive register fixtures and emulator barriers do not validate physical cache invalidation or bus synchronization.

## Cancellation, completion and IRQ composition

Sequence0 has an explicit cancellation branch when timer15 is enabled and requested profile equals200002A4(last state before timer start). It adjusts TON, restores target VDDC, stops the timer, sets pending26 and returns. It does **not** run normal completion2b/7b, perform full rail switching, or publish new target globals on that path.104 additional fixtures cover matching-profile cancellation and cache branches beyond its336 common cases.

Sequence7 starts a50us interval and sets pending7; explicit sequential7→completion tests apply saved trims, perform optional HP/LP/domain changes and stop the timer. Sequence21 sets continuation byte20074F77 and performs its first phase; explicit21→post→21b tests establish that21b selects trims from **current profile200002A0**, not pending target200742E8, and clears that continuation flag. Tests include an intentionally changed current profile to distinguish these inputs. These composed calls are synthetic sequencing, not observed IRQ/task ordering.

The locked main vector table word98 at438188 is `0x4D58A7`, corresponding to externalIRQ82. Original software call chain:

```text
locked main IRQ82 vector
  -> 0x4D58A6 timer15 vector wrapper
  -> 0x48039A registered timer service
  -> callback table20073270 slot11 (word2007329C)
  -> 0x5A40CA PCM2.2 boost completion, when that family is registered
  -> 2b or7b according to pending byte20004540
  -> timer stop0x4802CE
```

The registered post-LP-to-HP wrapper0x4803DC reads slot10(word20073298), calls it if non-NULL, otherwise returns0. The PCM2.2 target is5A40B6(post wrapper)→5A3E24(21b). New36 vector-wrapper,36 registered-timer and24 registered-post tests include NULL/non-NULL callbacks, pending2/7/26, absent/last/peer clock ownership and PRIMASK fixtures. Native fixtures install the corresponding native callback in synthetic SRAM; original fixtures install the actual original callback. This is test setup, not a firmware callback-table patch. Calling the vector instructions as an ordinary function does not emulate NVIC exception entry/return, prove runtime VTOR, or observe live delivery.

## TON provider and data layout

TON provider0x5A423C is now independently reconstructed, linked into every native table body and directly compared in288 fixtures. Selectors0..6 read5-bit calibration fields; selector7 preserves/reuses existing MMIO trim fields. Profile8 forces selector7. Otherwise-unhandled selectors use selector5's field layout. Direct cases include0..9,100,FFFFFFFF, profiles0/7/8/19, and zero/mixed/all-one calibration plus MMIO patterns. This internal control selector is not a BLE wire opcode.

|Data|Recovered layout|
|---|---|
|20056660+4×profile|Calibration word: VDDF[6:0], coreLDOactive[16:7], tempco[20:17], VDDC[27:21]|
|200566C0|Four packed7-bit low-voltage trim adjustments, selected by profile&3|
|200742D4/D8/DC/E0|Pending VDDC/VDDF/coreLDOactive/tempco uint32 fields|
|200742E4/E8|Pending TON/power-profile uint32 fields|
|200002A0/A4|Current profile/last profile before timer|
|20004540|One-byte ongoing sequence;2/7 handled,26 invalid|
|20074F77|One-byte deferred21b continuation|
|20073270+4×slot|Registered family callback table; slots10/11 are post/boost service|

The complete header includes the sealed sequence2/fixed-width pending-state interface. Build explicitly selects `-fshort-enums`; byte state stores remain `uint8_t`, so default host enum ABI is not assumed. The prior441-input public-leaf compact-versus-wide enum evidence remains sealed and is not extrapolated to all upstream structs.

## Primary sources and practical submodule status

[Ambiq HAL](https://github.com/AmbiqMicro/ambiqhal_ambiq/tree/5efc0228528a8adce5eae0d226fac85d2551eb3b/mcu/apollo510/hal) is pinned to `5efc0228528a8adce5eae0d226fac85d2551eb3b` at existing registered gitlink `third-party/upstream/ambiqhal-apollo510`. New useful [ARM CMSIS5.9 headers](https://github.com/ARM-software/CMSIS_5/tree/2b7495b8535bdcb306dac29b9ded4cfb679d7e5c/CMSIS/Core/Include) were downloaded sparsely at existing registered gitlink `third-party/upstream/cmsis-5-590`, pin `2b7495b8535bdcb306dac29b9ded4cfb679d7e5c`. HAL cache source and CMSIS cachel1/core_cm55 headers corroborate the guard and inline cache instruction sequence. [Pinned hashes and actual reference status](source-reference.json).

Both reference directories are clean standalone sparse Git checkouts at their indexed gitlink commits and are usable locally. Root `git submodule status` still shows a leadingminus because normal root-configuration enrollment was deliberately untouched. This is source materialization, not a claim that conventional `git submodule init` finished. No.gitmodules, root index or root Git configuration was changed. Original vendor license notices remain in the reference checkouts; the new C is independent stock-instruction reconstruction.

## Validation limits and next source leads

Every final receipt binds the same ELF and current source/header hashes. Stock delay/ITCM, timer-start, clock-release, status-poll and IRQ-save code executes; TON and cache providers are independently reconstructed and tested. No successful external-return stubs are substituted. Observables are ordered MMIO writes, logical helper call arguments, selected globals/clock-client bitmap, state bytes and PRIMASK; all memory reads, scratch-register clobbers and cycles are not compared. IRQ/cache effects are passive. M33-compatible ARMv8-M/FPU execution covers the selected M55 subset, not full M55 exceptions. Calibration words are synthetic, with no authentic device values inferred.

For CFW/app work, this explains why a power update can have a delayed second phase, why void/success-looking calls do not prove settled rails, why cancellation differs from finishing pending work, and why replacing the stock routines with public SDK macros can change behavior. Live quiescence and ownership decisions still require coherent current-profile/calibration/timer/IRQ/task-state evidence.

No table-body source lead in this selected PCM2.2 family remains merely opaque. The wider source search is **not exhausted**: pinned PCM0.7/2.0/2.1 variant bodies and actual CPU power-mode wrappers/callers remain useful distinct targets. Authentic calibration values are required to identify the device's runtime variant/trims; a coherent exception/task trace is required for physical timing/IRQ/RTOS conclusions. No tools/input blocked this static family recovery, and no hardware safety/firmware completeness claim is made.

Navigation: [registration/classification/planning and ITCM correction](../audio-platform-callbacks-closure-2026-10-08/REPORT.md); [sequence2 and completion/timer lifecycle](../audio-transition-timer-closure-2026-10-08/REPORT.md); this report covers the remaining table bodies and native TON/cache/registered/vector wrappers. Prior sealed reports, audit inputs, checkpoints, index and campaign remain unchanged. No commits, production edits or device writes.
