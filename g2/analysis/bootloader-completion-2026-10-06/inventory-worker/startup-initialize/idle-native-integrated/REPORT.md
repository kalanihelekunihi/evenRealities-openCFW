# Native idle/sleep214-object successor — completed bounded validation

The separate candidate is `g2/build/bootloader-completion/idle-native-integrated/badad5a92beec12dd1f5389033d51db87aa8d5bb77cb3410a7e465f2aa649b57/candidate.elf`.

All seven exact-image integration fixtures PASS: two normal/update, three malformed-input, two interruption/power-loss. The validation summary records65 PASS receipt files, including44 inherited broader regression suites,528 original-instruction idle/lifecycle comparisons, six bootstrap installation fixtures,260 runtime,512 teardown,24 idle cleanup, actual allocator/heap drain, selector1/3/17,1400 initialized-root,96 scheduler-resume and288 tick comparisons. Fixture counts are not coverage percentages. All214 frozen object hashes match. Re-linking their preserved order/basenames with the frozen linker reproduces the exact candidate hash. Six isolated component copies compile to byte-identical frozen objects; the CP setter return declaration was corrected without changing machine output.

The bootstrap now installs a compiler-resolved native idle PC. Its comparison normalizes only that relocated frame PC; guest frames are not changed. Native idle invokes actual cleanup, suspension, scheduler resumption and critical-section implementations. The recovered41a71e deep-sleep body manipulates CPDLP, silicon/PCM power flags, buck/trim overrides, bus flush and WFI, restores power/CP configuration and PRIMASK, and may service a pending boost timer and sleep again. Exception0x62 is an exception number; no timing units are inferred from it. STIMER sampling/compare uses counter counts, while scheduler inputs remain ticks.

## Evidence limits

This is an unpromoted offline three-slot layout; `.source_idle` is2288bytes at0x50000 in a declared64KiB test slot. Original two-slot ELF reader is unchanged. The owned adapter adds that slot and splits overlapping existing mappings without changing test assertions. Harness first attempts are preserved: missing inherited fixture files, predecessor hash pins, and third-slot overlaps were corrected. Final adapters/drivers are hash-pinned in validation-source-addendum.json; creation manifests remain untouched.

Power-state/boost bodies remain external-call contracts in this candidate; WFI wake is synthetic in the528-case chain. Deep-sleep original coverage is1284/1318bytes, not complete branch coverage. Bootstrap timer/port calls are symmetric test cuts. The separate nine-case QEMU M55 harness proves modeled architectural exception/FP handling on MPS3, not this candidate's physical Apollo sleep or peripherals. Inherited enum-attribute linker warnings remain; new provider interfaces do not exchange enum-valued arguments. Resident ROM, hardware timing/concurrency, full source completeness and locked OTA byte equality remain open.

## Next source frontier actually investigated

Pinned official Ambiq SPOT manager/PCM sources were acquired under `upstream/`, retaining file copyright/license notices and provenance. The repository already pins this upstream as `third-party/upstream/ambiqhal-apollo510`; no index/submodule metadata was changed. Independent wrapper work and a negative SDK match are in sibling `spot-sleep-wrappers/REPORT.md`. This evidence is actionable and not exhausted; the ranked local continuation queue is `upstream-hypothesis-queue.json`.
