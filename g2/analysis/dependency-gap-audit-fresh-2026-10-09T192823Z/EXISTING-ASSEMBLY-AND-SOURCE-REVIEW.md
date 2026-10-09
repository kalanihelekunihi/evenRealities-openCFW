# Bounded existing ARM assembly and source-rebuild review

Existing selected original listings support the following authenticated, deduplicated byte representation. These are additional bounded measures; the earlier six-component matrix’s unknown whole-executable assembly fields remain unknown.

| Component | Unique serialized original bytes | Full stored payload fraction | Whole-executable assembly coverage |
|---|---:|---:|---|
| apollo_main | 17,484 | 0.50% | Unknown |
| apollo_bootloader | 9,594 | 6.46% | Unknown |
| touch | 15,616 | 45.31% | Unknown |
| case | 4,320 | 7.74% | Unknown |

[Verification receipt](EXISTING-ARM-LISTING-VERIFICATION.json) includes image hashes, per-file hashes, counts, component payload-coordinate unions and candidate inventory. The scan includes ignored/hidden artifacts, selects 114 existing original-labelled ARM listings plus the original bootloader startup disassembly, and excludes public/native assembly, pseudocode ranges and this audit’s earlier full linear dumps. No new disassembly was generated. GNU-banner ARM halfword tokens and Capstone byte strings were decoded by their declared format; zero byte mismatches remain. Eight touch data-directive byte occurrences were excluded. Overlaps count once; decoded RAM copies and unrelated addresses do not add flash bytes.

This converts selected-listing representation from unknown into measured bytes. It does not certify every counted instruction as executable: original linear decoding can include literal pools/data, and the listings do not provide a complete independently audited executable/data partition. Missing input for whole-executable percentages is that partition plus a complete admitted listing receipt, rather than another raw linear disassembly. Existing selected listings are present for all four components, so claiming assembly is absent would be incorrect.

[Independent function-count verification](FUNCTION-COUNT-INDEPENDENT-VERIFICATION.json) authenticates every successful nonempty output and unique function row: legacy Apollo 7,449/7,449; bootloader 849/903; touch 308/308; case 435/435; five codec exports 929/929. Apollo’s larger partial-union cohort remains separately 8,475/8,853. Successful discovered-function coverage is not full-payload byte coverage, semantic review, or C compilability.

## NationalChip source-assembly reproduction

The owner’s `../nationalchip-dsp-source-rebuild-20261009T194601Z/assembly-results.json` now records successful preprocessing and target assembly of seven original source files. Independent read-only extraction authenticates the source hashes, assembler hash, seven produced ELF objects and nine relocation-free text sections against original codec bytes. [Receipt](DSP-SOURCE-ASSEMBLY-INDEPENDENT-VERIFICATION.json): 17 checks pass, nine unique sections / 1,606 bytes / 0.4925% of codec payload. This is stronger than archive correspondence: selected source-assembly output is now reproduced. It remains **assembly source**, not C compilation or an integrated source-only image. No source/build percentage in the canonical matrix increases.

The separate [FFT table receipt](FFT-TABLE-INDEPENDENT-VERIFICATION.json) verifies 2,272 exact table bytes and the explicitly unequal relocated descriptor. Tables and source-assembly sections are distinct provenance measures and must not be merged into a C-compilable percentage.

The discovery track’s currently available Pigweed packet remains a protocol reference. Its bounded HCI201C request/consumer offsets were already independently resolved; it supplies neither the producing firmware SDK nor physical controller capability. No newer discovery packet was present at this review snapshot.

No new build was run by this audit, and no sealed evidence, source, canonical ledger, Git, device or production state was changed. Tool limitation: a redundant slow file scan could not be stopped with `pkill` because the host lacked its process-list service; it subsequently completed, and the authoritative verifier reran with the correct declared serialization formats. No approval rejection or model change occurred.
