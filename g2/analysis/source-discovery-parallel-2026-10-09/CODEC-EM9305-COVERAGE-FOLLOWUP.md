# Codec/EM9305 finite mapping follow-up

Only existing artifacts read. No decompilation, build, admission, canonical changes or queue execution.

## Codec raw export unions

All929 bounding-envelope hashes freshly match canonical terminal images; all five run image hashes match. Body range unions count overlapping bytes once, and only decompiled=true records with existing exports enter the numerator. Offsets are image-local, avoiding runtime alias double counting.

| Image | Image bytes | Records | Raw export union bytes | Image fraction |
|---|---:|---:|---:|---:|
| uart_stage1 | 10240 | 32 | 3142 | 30.6836% |
| uart_stage2 | 27964 | 96 | 11498 | 41.1172% |
| binh_a_stage2_xip | 36484 | 362 | 28962 | 79.3827% |
| binh_a_stage2_sram | 14716 | 151 | 11313 | 76.8755% |
| binh_b_stage2 | 82060 | 288 | 37645 | 45.8750% |

Total92560bytes are associated with raw exports,28.3846% of the326092-byte codec payload. This is a partial artifact mapping, not reviewed pseudocode completeness. Two12288-byte main stage1 images have no mapping in this five-input export cohort. NPUcommand9164 andweights120800 are separate model/accelerator regions; neither is automatically MCU executable code. Wrapper/container bytes and SRAM/data boundaries remain separate. Source/load coordinate facts remain conditional where previously qualified.

## Assembly listing unions

EM9305 whole payload SHA91a38f7fc05555f86181ecb22b363e3239bfcaaa2ff6171e98524ae64821eca9 verified. The generator explicitly maps package bytes at0x301FDC; record3 file offset1060 therefore maps to0x302400. This establishes the generator's byte coordinates, not an independently proven silicon load map. Parsed listing halfwords match raw bytes with zero mismatches. Unique listed bytes210072:99.6131% of record3's210888bytes,99.1149% of whole211948-byte payload. Record3 has816bytes not represented by parsed address/byte lines. Metadata/other records total1060bytes are outside this listing scope. Data may be rendered as instructions; no executable denominator is inferred.

Codec XIP listing matches all36484 image bytes after correctly interpreting objdump's32-bit displayed words as ordered little-endian halfwords. Thus100% of this image has a byte-matched raw listing,11.1883% of the codec payload. Visible literal words are also decoded; this is **not100% assembly semantic coverage**.

The initial receipt `codec-em9305-range-unions.json` is retained: its C-SKY decoder reversed whole32-bit words and reported3775mismatches; it is FAILED for C-SKY listing accounting. `codec-em9305-range-unions-corrected.json` fixes halfword serialization and has zero mismatches. EM and codec pseudocode results were unchanged. Both preserve exact interval unions and input hashes.

## Finite remaining blockers

1. No consolidated accepted-review-to-interval map was found for the targeted EM9305 decompilation rounds; filenames/status fragments cannot safely supply a whole-record pseudocode numerator. Deduplicate rounds and verify their input pins before counting.
2. The816 EM bytes absent from parsed listing lines need explicit gap/data/padding/undecoded classification; do not call them missing instructions. Exact represented unions are saved for complement computation.
3. Current reviewed semantics, decoder unsupported operations, literal/data intervals and failed/superseded reviews still need joined accounting. Listing byte equality authenticates representation only.
4. Main codec stage1 images and remaining terminal images need separately scoped existing listing/export inventories. The current XIP-only assembly result cannot be extrapolated to all codec images.
5. Four Arm raw unions from the preceding report remain authenticated partial mappings; their saved complements require code/data classification before executable percentages.
6. R1 mapping and source/compiler input-span maps remain separate tasks; blob-array emission and upstream availability cannot establish C completeness.

These findings close codec five-input raw hash/union mapping and EM/XIP listing byte mapping, while leaving semantic coverage denominators explicitly unresolved.
