# PCM2.2 native startup follow-through

Locked input: `g2/blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin`, SHA-256 `f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5`, loaded at `0x410000`, ARM Thumb. Final standalone candidate: `370bdfaad92ffb7fca2a7e24d9950ab1ceebb071ef8238d357d6f6c722079598`, frozen with 197 linked objects under `g2/build/bootloader-completion/startup-pcm22-native/<hash>/`. This is reconstructed source, not byte-identical producing source. All seven integrated cases,38 inherited regressions,eight additional native behavioral suites and alignment reconciliation PASS on this exact candidate. The shared promoted checkpoint remains129a; this standalone root result does not retire its broader startup alias.

## Concrete recovered behavior

PCM2.2 is Apollo510 silicon power control, not EM9305 or GX8002 controller firmware. The runtime chooses this callback family for revision >=36, or revision35 with variant >=2. The callback dispatcher, selector and transition walker now link real native source. The observed startup matrix requires selectors0,2,14,18,24; other stored targets remain unresolved contracts guarded against execution in this matrix.

- Selector0 (`0x427e84`,470 bytes): prepares target cached trims, adjusts TON, boosts VDDF with saturation, switches cache/override state and updates core trim. Core temperature compensation occupies register `0x40020080[13:10]`; active trim occupies `[9:0]`, with two ordered RMW writes. The cache/timer paths are compared, including the cached-target early branch.
- Selector2 (`0x428240`,312 bytes): completes a prior pending timer sequence if enabled, records new target trims, adjusts TON, writes the profile value at `0x20026ba0+0x50` directly, ramps VDDC, records target state and starts a deferred timer sequence. The stock body has no public-source delay(10) at this point.
- Selectors14/18 (`0x42944a`,210 bytes; `0x42984e`,464 bytes): wait/service the existing timer before updating trims.14 returns the four packed low-seven-bit VDDCLV fields through its original stack return convention;18 returns the target profile pointer.18's ordered boost/delay/restore writes are compared.
- Timer start (`0x41cc48`,74 bytes) programs compare `wait*6`, requests the real clock provider, programs timer/NVIC and enables bit0. No milliseconds conversion is claimed. Stop (`0x41ccd6`,68 bytes) disables timer/IRQ, clears pending state and releases its clock.
- Timer service (`0x42a04a`,46 bytes) dispatches pending-state byte2 or7 to helpers2b (`0x428378`,106 bytes) or7b (`0x428a94`,276 bytes), then stops the timer and restores PRIMASK. State26 is the completed sentinel. Actual stock ISR instructions unconditionally restore PRIMASK; an inferred Ghidra privilege branch was rejected.
- Timer enable is `0x400083e0 & 1`; readiness is `0x40008064 & 0x40000000`, proven by the original LSL instructions. The prior bit31 assumptions failed timer-enabled fixtures and are preserved as counterexamples.

Public Ambiq PCM2.1/2.2 C at pin `5efc0228528a8adce5eae0d226fac85d2551eb3b` supplies hypotheses and BSD-licensed algorithms. Stock differences are retained: state20 rank words, timer/helper delays, temperature controlflow, profile selection and register layout. Public macros are not proof of this locked image.

## Source and execution evidence

- `timer_support.c`: six reconstructed helpers; `pcm22_interfaces.h`: recovered helper/sequence contracts and verified masks.
- `../../startup-events-a/` (actual sibling under inventory-worker): `startup_events_a.c`, trim/selector/walker sources, `startup_event_a_sequences_0_2.c`, `comparison-root-handlers.json`.22 strict original/source pairs on final370, including ordered SRAM/MMIO, return/IRQ/SP, ROM-delay input, timer/cache modes and pending states.
- `../pcm2_2-handlers-14-18/`: `handlers.c`, `comparison-timer-enabled-final.json`.56 pairs on final370; all210/210 and464/464 original body bytes visited. Mask failure preserved.
- `root-initialized-comparison.json`: all1400 stock/source startup fixtures with recovered rank arrays and initialized state20, additional PCM SRAM snapshots; zero excluded variants. All810 root-body bytes visited. The prior368 excluded cases now participate.
- Final baseline-state root and864 helper cases are in the frozen candidate's copied validation receipts after reconciliation. Helpers visit all626 original body bytes.
- `root-before-pcm22-fix.failure.json` preserves the first full-root counterexample: wrong core trim register fields/order and an extra public-source delay. `first-native-attempt.json` binds it to the failing image hash. Prior PCM2.1 trim-cache failure and old candidates remain in `../gx-native/`.

## Limits and next actionable lead

Root fixtures seed the authenticated callback table and replace the five observed entries with source addresses; they do not prove a complete source relocation/initialization implementation for every selector. Source-side execution of every raw selector entry is rejected. The root/clock call chain executes reconstructed dependencies rather than callback-success stubs, with resident ROM40/48 and synthetic peripheral acknowledgment/readiness as external boundaries. Direct handler fixtures preserve the ROM delay boundary. None establishes real timer interrupt timing, concurrent scheduling, hardware drain or hardware safety.

The main integration startup/logger models remain explicit. The selected main-linker startup alias is still `0x41c4b5`; this separate root closure does not silently retire that broader interface contract. Remaining PCM2.2 selectors outside the observed startup matrix, decoded initialization relocation, unavailable ROM/SBL/NOR and producing compiler/configuration remain distinct gaps. Byte equality, source completeness and bounded behavioral tests are separate.

Next actionable source experiment: selector8's timer-enabled branch. Its prior timer-disabled port and400 comparisons are preserved; a successor is being developed separately and will not mutate final370. Other original selector bodies and pinned PCM algorithms remain actionable, so dependency exhaustion is not claimed. No commits, hardware writes or credentials were used.

## Completed dependency follow-ons kept separate

Selector8's full timer port is `../../startup-events-a/startup_event_a_sequence8_timer.c`, with24 strict cases in `comparison-sequence8-timer.json` on successor `fe48705a…`; prior400 timer-disabled cases remain passing. The first delay-before-poll ordering hypothesis was rejected by the original instructions. This successor is not substituted into final370's integration receipts.

Selector15 is in `../pcm2_2-handler15/`: entry429524,256 bytes,SHA-256 `b9c0d1de31402701d130b56442cb955fe92c59ce4973cfc4a79652df8a6e23be`.14 strict cases visit all256 bytes with timer/profile variation. Its stock stack epilogue returns R0=packed low-trim bytes and R1=incoming fourth argument; the C reconstruction uses a64-bit return to preserve both. The separate addon is linked to final370's symbols and loaded with that authenticated base; its direct proof is not a complete integrated successor proof. Source/data/wait/order and ROM boundary remain explicit in its receipt.

Current dependency queue: assemble selectors8/15 into a separate successor, validate new walker/callback reachability with nonuniform profiles, then port selectors16/17 or the next actually reached target. Other selectors and full recovered-data initialization relocation are actionable. Missing ROM/hardware scheduling traces limit physical claims but do not block these source experiments. Current hypotheses are not exhausted.

Navigation: `../gx-native/` (PCM2.1 root/trim bug and compressed-data provenance), `../../startup-events-a/` (PCM2.2 selector/walker,0/2 and8), `../pcm2_2-handlers-14-18/` (14/18), this directory (native helpers/root/runtime/header/validation), `../pcm2_2-handler15/` (15). `candidate-validation.json` indexes all final370 receipts and frozen-input reconciliation.

Fixture count precision:0x1a equals26. The0/2receipt has22 executed comparisons across18 distinct tuples; selector8 has24 executions across18 distinct tuples. Original receipts are preserved; `fixture-distinctness.json` records this reconciliation. Neither duplicated run adds new coverage.
