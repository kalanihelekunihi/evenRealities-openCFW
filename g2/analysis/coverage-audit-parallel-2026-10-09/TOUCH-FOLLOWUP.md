# Touch Configure and unavailable-source follow-up

The inspected evidence retains the mismatch; no later resolution was found before this investigation stopped. Owner task `01a0f4a0-6c2a-70e7-8394-b1e0c936f028` owns source changes and experiments. This audit proposes discrimination only, and performed no compilation or sealed-test rerun.

## Exact current evidence

[receipt.json](../touch-msclp-attribution-2026-10-08/receipt.json) pins PDL `35f1714623cfea682d5e285af80d50416b4c7bbc`, `cy_msclp.c` SHA-256 `2613ec6fee3ac2ca6d8a42e483bb671f9ed63a58045b125ee6fe11f6f2d60f07`, GNU 13.3.1 build arm-13.24, Cortex-M0+, Thumb, freestanding/no-builtin, device CY8C4046FNI_T412 and function sections. Configure at `0x8fd0` has stock extent 424 bytes; the `-Og` object also has 424 bytes and 158 identical prefix bytes. The recorded difference is 24 bytes in loop layout. ConfigureScan at `0x9178` matches all 160 bytes. Capture at `0x8fa0` matches all 48 bytes in the [reproduction receipt](../touch-msclp-attribution-2026-10-08/reproduction-receipt.json).

Already tested and therefore unsuitable for duplicate experiments:

- GNU 13.3 `-Og`, `-O1`, `-O2`, `-Os`. Configure sizes respectively 424, 404, 396, 388; only `-Og` preserves stock size.
- [loop-screen.json](../touch-msclp-attribution-2026-10-08/loop-screen.json): `-fno-tree-ch` and `-fno-thread-jumps` produce the same Configure hash and 24-byte difference. `-fno-guess-branch-probability` produces 436 bytes and 384 mismatched bytes.
- The 180 original/public behavioral cases in the original report; later 348 preparation comparisons compose the public body without admitting byte equality.

[regular-mode composition](../touch-regular-mode-composition-2026-10-08/REPORT.md), [auto dither](../touch-auto-dither-closure-2026-10-08/REPORT.md), and [scan preparation](../touch-scan-preparation-closure-2026-10-08/REPORT.md) all expressly retain the mismatch. No inspected receipt promotes Configure to exact source attribution. The separate 6.10 CapSense source pin matches its cached release bytes; this does not resolve PDL Configure compiler provenance.

## Competing explanations and smallest new experiments

| Hypothesis | Existing support/limit | Minimal discriminator for owner |
| --- | --- | --- |
| Older GCC code-generation choice | Touch `Cy_SCB_ReadArrayNoCheck` matches GCC 10.3–13.3 at `-Og`; it does not discriminate these releases | Compile only unmodified pinned `cy_msclp.c` with 10.3, 11.3, 12.2 at the exact recorded flags/include hashes. Extract Configure plus Capture/ConfigureScan from the same object. No behavioral harness needed. Require complete section equality and no unhandled relocations. |
| Producing PDL source differs in the loop | Same extent and large matching prefix support close lineage, not identical source | First compare the specific Configure loop across already-present PDL candidates using source hashes/diffs. Compile only genuinely different loop revisions; do not redownload identical sources or sweep unrelated versions. |
| Translation-unit/header/macro environment differs | Receipt uses an explicit system header stub and pinned includes; original full build flags remain unknown | Preserve preprocessed input and compiler pass/assembly output for a new compiler candidate. Compare the mismatching loop against its actual source/type/volatile definitions before any targeted environment change. An arbitrary patched loop is not provenance. |
| Generated cycfg changes this no-external-call body | Configure accepts runtime config; current public body has no external-call relocations | Low-priority explanation for this local code-layout mismatch. Generated config remains relevant to whole-image reconstruction, but it should not be cited as the immediate cause without showing a compile-time dependency in preprocessed input. |

If all three older GNU objects retain the mismatch, the experiment narrows the stated compiler hypothesis without proving a private source modification. If one matches Configure but fails peers, it is incomplete compiler evidence. If all peers match, it is a better candidate, still not a uniquely authenticated producing toolchain. Do not manually adjust instruction scheduling or byte-patch outputs and call it original public-source attribution.

## Sources actually present

The current inventory surfaced `third-party/local-vendor/iar-base-container-build/cxarm-10.10.2/arm/src/lib/dlib/DLib_setup.h` and `rtsl/fenv.h`, plus DLIB product/C++ headers. Therefore a blanket claim that no IAR/DLIB material exists locally would be false. These observed support files do not prove complete runtime implementation source, and the version is 10.10.2 rather than the missing candidate 9.60.2. Availability of the exact required runtime remains unverified by this partial inventory.

`third-party/upstream/lvgl/libs/nema_gfx` has Nema API headers and Cortex-M33 GCC `libnemagfx*.a` archives. LVGL also has Nema integration C files. Thus Nema reference interfaces and prebuilt binaries are present; these are not implementation source corresponding to the linked IAR objects. No contradiction to the narrowly stated unavailable matching implementation-source claim was established.

The expected root PDL source path `third-party/upstream/infineon-mtb-pdl-cat2/drivers/source/cy_msclp.c` was absent, while the receipt's pinned `/tmp/opencfw-touch-source/mtb-pdl-cat2-35f171...` checkout appeared in the inventory. Do not assume registry checkout presence from a pin alone; use the authenticated receipt path or an owner-verified equivalent.

## Stop and limits

A broad read-only `rg --files /tmp` inventory reported `Operation not permitted` for `/tmp/codex-daemon-501`. Investigation stopped on that access denial as requested, without escalation or model switching. The denial concerns an unrelated daemon directory; no conclusion about missing dependency source follows from it. No further dependency inventory or detailed object disassembly was attempted. Conclusions above are bounded by the inspected receipts and filenames; exact loop instruction offsets, source revision alternatives, current compiler availability and exhaustive unavailable-source status remain for owner verification.
