# Independent case label and callback visibility review

29 independent stdlib checks passed in CASE-CALLBACK-VERIFICATION.json, reproducible with case_callback_verify.py. No sealed tests were rerun, instructions executed, sources compiled, hardware accessed, or canonical files changed.

## Case FLASH correction

Authenticated all four inputs in the owner packet, both full 28-byte extents, all 28 listed Thumb instructions, and six PC-relative literal loads directly against package bytes. The historical labels are reversed: 08004B6C is HAL_FLASH_OB_Unlock (OPTKEYR +12, bit30, keys08192A3B/4C5D6E7F); 08004BF4 is HAL_FLASH_Unlock (KEYR +8, bit31, keys45670123/CDEF89AB). The official pinned HAL source supports both volatile CR reads and asymmetric already-unlocked status: OB returns HAL_ERROR; ordinary unlock returns HAL_OK. The observed branch/sign tests agree. This is a concrete correction of 56 existing code bytes, not 56 new source-rebuilt bytes. Whole-source equality, MMIO delivery and exact producing configuration remain unproved. Owner REPORT.md is justified within those limits; historical TSV was preserved.

## Callback initialized descriptor

Freshly authenticated canonical SRAM and XIP images, root hash/pointer, all eight descriptor words, three strings, four exact XIP root-pointer literals and package root offset18D4C. Stored10026D38 contains20026D3C; AppInit10208E4C, event10208F04, loop102091BC, suspend10208DEC and resume10208DCC are available static targets. Descriptor and strings agree with public sample-app field ordering. Strings/pattern do not select a unique source revision/application. Earlier boundary language implying unavailable callback addresses is stale; the unresolved quantity is runtime visibility/content and effects. Exact-pointer search cannot exclude computed writes.

## Visibility stop boundary

Independently authenticated all five visibility-contract inputs and inspected actual linker/SPL source. Linker places initialized data and BSS in stage2_dram; normal SPL computes text length plus data length and passes the IRAM text start as one flash-read destination before jumping. Alternate source explicitly writes DRAM and jumps IRAM. This corroborates a platform address-space dependency, without defining its semantics. The sealed SRAM image is14716 bytes; root/descriptor lie inside [10023400,10026D7C). The linker/loader data boundary264E4 versus aligned section boundary264E8 remains a four-byte distinction, with no bearing on root inclusion.

CALLBACK-VISIBILITY-STOP-BOUNDARY.md is justified as a bounded static gap, not runtime-only or source-unavailable closure: a platform translation specification, normal-path address-translation configuration, or authenticated loader/helper write contract can still supply static evidence. Source intent and numeric1002/2002 offset similarity do not prove aliasing. Startup/main call claims in CALLBACK-ROOT-STATIC-INITIALIZER.md are existing decoded packet evidence; this review does not claim new independent full startup/callee semantic closure. No universal absence of indirect copy paths, actual DRAM contents, flash-read success, entry execution, callback dispatch or hardware effects is established.

## Exhaustion assessment

The label-correction branch is closed for the demonstrated static discriminator. Callback descriptor discovery materially advances an earlier stale lead, while runtime address visibility remains an explicit static opportunity requiring new evidence. Thus these packets support local progress, not exhaustion of declared G2 goals, full reviewed pseudocode, source completeness, or bundle byte equality. Existing component matrix and final scope reconciliation remain applicable.

Evidence: ../case-flash-unlock-label-correction-2026-10-09/REPORT.md; ../source-discovery-parallel-2026-10-09/CALLBACK-ROOT-STATIC-INITIALIZER.md; ../source-discovery-parallel-2026-10-09/CALLBACK-VISIBILITY-STOP-BOUNDARY.md. Verification references every hashed input by repository-relative path.
