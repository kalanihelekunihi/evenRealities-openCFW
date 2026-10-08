# Native PCM2.2 CPU/hot-state transition reconstruction

Separate 220-object offline candidate SHA-256 e5972f996f4ffc9a08ac54ba8e92e07cbc1745425db32b1eb78a9c9dea67b7ff. Four requested callbacks5,11,12,21 are reconstructed and compiler-installed; preserved218-object82039de1 and shared129a6b2f are not replaced. All7 exact-image integration cases PASS:2 normal/update,3 malformed-input,2 interrupted-update. Final component copies are delivered in g2/components/bootloader/initializer_callbacks/pcm22_hot_native/ and reproduce frozen objects exactly.

## New understanding and source

| Selector | Locked range | Body bytes | Concrete behavior |
|---|---|---:|---|
|5|42863e..428840|514|Matched pending-timer target adjusts TON/VDDC then stops timer and returns early. Otherwise switches LP, clears CPU/AOR overrides, conditionally switches HP, loads CORE/VDDC.|
|11|428e6a..4290a2|568|Hot-state transition switches LP/HP, loads CORE/VDDC, double-boosts VDDF with saturation, waits50, restores VDDF, adjusts TON last.|
|12|4290a2..4291e0|318|Boosts VDDF, loads CORE, waits50, restores VDDF; no locked TON-adjust call.|
|21|429c46..429d9e|344|Sets continuation byte, adjusts TON, boosts/restores VDDF, conditionally disables I-cache, selects CPU/memory status bits, waits20, restores cache request.|

Readable reconstruction is delivered in the component directory above and preserved in the two owned analysis areas; interfaces.h explains fields and private ABI. Direct byte-backed disassembly/function hashes are local. These are four newly closed bodies totaling1744 original instruction bytes; reused DATA/updater variants are not newly reconstructed functions.

The pinned official Apollo510 SDK identifies this family and sequence names. Locked instructions govern differences: selector11 adds VDDF boost absent from the cited SDK counterpart; selector12 omits the SDK TON call. Dependency ordering, ignored poll/cache errors, profile rereads and native providers are in DEPENDENCIES.md. No opaque callback return was substituted during new direct/updater comparisons; resident ROM delay40 alone is stubbed. Delays/readiness are synthetic, not hardware measurements.

## Validation already completed

579 original/source selector5 cases cover all514 bytes.796 selector11/12/21 cases cover all568/318/344 bytes, including decreasing/increasing/saturating trims, enabled/disabled timer, ready/timeout conditions, cache active/inactive and cache-helper rejection. Observables include rawR0, stack/callee-saved registers, ordered MMIO and selected persistent SRAM writes, and resident-ROM delay inputs.192 predecessor selector20 cases also pass on this image.

151 completed native updater frontier cases plus17 targeted installed-updater cases PASS; none stops on the four previously unsupported selectors. They exercise actual DATA installation, dispatcher, wrapper, state determination and callback bodies. Their union visits756/758 updater bytes through selectors0/1/2/3/5/6/11/12/14/17/18/20/21/24. Overlapping fixtures and visitation are not source completeness metrics.

290 Cortex-M55 QEMU comparisons using the exact frozen source object match bucket and full rawFPSCR; preserved bit-helper negative control still has8 bucket/290 FPSCR differences. No result masking or FPSCR repair. Frozen-object relinking reproduces the exact ELF;220 input hashes reconcile. Four final C sources reproduce frozen objects exactly. Corrected declarations change no object bytes; final source hashes are recorded separately from immutable creation copies.

44 broad,11 focused,5 extra and3 closure driver runs finish successfully. First copied-verifier hash/mask/binding pin rejections and a missing synthetic cache register mapping are retained in diagnostics.json and focused attempt receipts. Only the affected pin-gated tests were rerun after final pin correction; candidate bytes did not change.

## The remaining two updater bytes

42aa1e is a real B.N42aa58 for a reread temperature-global value above4. Static classifier return range is0..4, so unmutated inputs do not reach it. Stock rereads global200271bd for flag/bounds decisions while retaining original class in the stack snapshot. Prior218 reconstruction cached the class and used class3 as its catch-all. This successor preserves both volatile rereads and above-four default behavior. Three synthetic mutations5/127/255 reach the real branch and leave bounds unchanged; tests stop at the actual downstream helper entry. They do not count toward completed updater coverage or prove a hardware race. See TEMPERATURE-DEFAULT.md.

## Limits and next boundary

Selector21 return leaves continuation byte200271bc set. Stock deferred body429da4..429df6 loads current CORE/VDDC and clears it; no source binding or complete deferred hardware lifecycle is added here. Reached native dependencies are closed for this fixture set, not all possible future transitions. Eight selector table slots remain unsupported in the owned binding manifest. Asynchronous IRQ/cache/FP context behavior, physical peripherals/ROM, general transition scheduling and raw flag-width ABI boundaries remain unverified. Source slots text65384/cache64284/idle5936 fit64KiB test slots; this layout is not a deployable Apollo memory map. No whole-source, byte-identical OTA or hardware-safe patch claim.

## Preserved navigation

- pcm22-power-integrated/:215-objectaac9ab01; earlier classifier bucket-only and callback-cut limitations retained.
- pcm21-selector6-integrated/:217-objectc528f8be; native selector6/boost integration.
- pcm22-fp-native-integrated/:218-object82039de1; native scalar FP and selector20, preserved290 QEMU checks.
- pcm22-selector5-integrated/:219-objectc7ffec17; bounded selector5 successor.
- This directory:220-objecte5972f99; all four requested bodies and native frontier closure.

All paths above are siblings under startup-initialize. Each identity is a separate offline checkpoint, not a replacement official firmware release. No commits/index/campaign/device writes.
