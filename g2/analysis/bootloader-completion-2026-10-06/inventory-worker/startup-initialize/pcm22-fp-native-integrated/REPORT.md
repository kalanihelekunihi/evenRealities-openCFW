# Native FP semantics and temperature-transition checkpoint

**218-object** separate offline candidate SHA-256 `82039de11491ebd971ba9b97d7eebb066f0b6a19f5cfad2a85d26295f2e0527f`. All**seven exact-image integration cases PASS** (normal/update2, malformed3, interrupted-update2). Broad44, focused11, extra5 and closure3 driver runs return0.218 input hashes reconcile and frozen-object relinking reproduces this ELF exactly. Three isolated component C copies compile to the frozen objects; they were created only after the seven cases passed. Existing217-object c528f8be… checkpoint/shared ELF/badad5a9… remain unchanged; no commits/index/campaign/hardware writes.

## What changed

Replaced bit-only temperature classification with scalar `VCMP`/`VMRS` and the original `BPL`/`BLT` flag decisions, preserving the compare sequence. No FPSCR writes or exception-mask fixes occur in the helper. Its original extent is0x427e0c..0x427e84 (118 bytes); source private ABI takes binary32 bits inR0 whereas original leaf takesS0. The compiled updater calls the private ABI; it is not a drop-in binary patch signature. FP register scratch, activation/lazy-context and asynchronous exception timing are not asserted identical.

A new reconstructed selector20 at0x429b4c..0x429c46 (250 bytes, SHA291e465a99bfa988f888524d1de3d093f6bf1b115aefacfb8bb8025284f23492) is compiler-installed in the DATA transition table; source mask0x717c14f. It waits/services the timer when enabled, updates cached TON/target/trim fields and CORE-LDO register40020080 in the stock order, then calls delay(5). Its delay/timer/downstream helpers already have native closure.192 direct exact-image original-instruction fixtures pass and exercise all250 body bytes; resident ROM delay40 alone remains stubbed. Delays/readiness remain synthetic, not measured elapsed hardware time.

The callback leaves a packed low-voltage word inR0, but the walker at0x42a43a discards callback returns immediately after BLX. This is not a firmware success/error status. Disassembly and function hashes are preserved; DEPENDENCIES.md records call flow and read ordering.

## FP evidence

**290 QEMU Cortex-M55 fixtures compare authenticated original classifier bytes with the exact frozen source object: bucket and full raw FPSCR match**, including all three previously mismatching signaling-NaN samples, FZ/DN, subnormals, reset LTPSIZE, sticky flags, QC and a rounding-mode setting. No FPSCR mismatch normalization occurs. The original604-byte code/literal reference slice is confined to the offline test oracle, never linked into the source candidate. fp-qemu/reproduce.py recreates both positive and negative controls.

The preserved c528f8be… bit-helper negative control fails the same290 comparisons with**eight bucket differences and290 full-FPSCR differences**.152 default-mode Unicorn comparisons now also match full FPSCR;108 mode comparisons match each other, but Unicorn's control/sticky behavior remains insufficient architecture evidence. Older discrepancies remain in the predecessor analysis, unchanged.

Official references are hash/revision-pinned under arm-reference/: Cortex-M55 TRM101051/0101 revision0101-03 supports FZ/DefaultNaN; [Armv8-M DDI0553B.z](https://developer.arm.com/documentation/ddi0553/bz), pages171–172 and1984, defines signed-zero flushing/IDC and NaN comparison/invalid-operation behavior. Scalar VCMP uses FPSCR controls and signals invalid for signalingNaN; the implementation delegates those effects to the actual instruction. This is bounded semantic evidence, not physical clock/exception-scheduling proof.

## Native updater closure

**145 completed frontier fixtures plus17 targeted installed fixtures cover756/758 updater bytes** through actual source callbacks, now including full default FPSCR in observables. No callback-cut receipt contributes coverage. Reached native selectors0/1/2/3/6/14/17/18/20/24. The two missing bytes0x42aa1e..0x42aa1f are a default branch after classification bucket tests; they are not marked covered. Overlapping fixtures/byte coverage are not a completeness percentage.

Six remaining paths are excluded from completed runs; both stock/source stop before the same unsupported selector:5 (CPU0->1/2),11 (temperature50/999),12 (deep-sleep temperature gate),21 (hot-state grid). Selector20 closes the cold-temperature path that was previously one of those boundaries. Next bounded dependency should be selector5 and its actual callees, followed by11/12/21. Raw direct-call flag-width behavior remains a separate ABI boundary.

## Deliverables and limits

Reconstructed C/header copies: `g2/components/bootloader/initializer_callbacks/pcm22_fp_native/`. Do not link the DATA/updater variants alongside parent variants. `startup_events_a.c` is readable reconstruction using documented scalar instructions; `pcm22_sequence20.c` is reconstruction from locked instructions, not unmodified SDK source. Function/image hashes, native coverage, official reference provenance, raw QEMU logs, retained negative controls and all exact-image receipts are indexed in `g2/build/bootloader-completion/pcm22-fp-native-integrated/82039de11491ebd971ba9b97d7eebb066f0b6a19f5cfad2a85d26295f2e0527f/validation-summary.json`; creation inputs remain immutable and final verifier versions have a separate hash addendum.

Source sections text65384/source_cache64284/source_idle4296 fit declared64KiB offline slots. This third-slot layout is not a deployable Apollo image. Resident ROM, synthetic peripherals/wake/readiness, asynchronous FP context behavior and remaining callback bodies limit conclusions. No source-complete or byte-identical OTA/hardware-safe transition claim.
