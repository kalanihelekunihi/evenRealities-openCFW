# Final reviewed fresh-scan successor

This additive summary supersedes stale unresolved rows in the earlier fresh-scan summaries. All findings bind the locked G2 2.2.6.10 image unless explicitly described as public-reference comparison. No repeated execution/probes, index/production changes or device operations were performed for this consolidation.

## Confirmed firmware knowledge

**BLE transport selects IOM6.** The independent review verified 3,069 checks including 3,032 instruction records. Derived base is `0x40056000`; GPIO ready reads `0x40010410` bank bit21, GPIO117, rather than dedicated BLEIF status. GPIO149 chip select, GPIO93 reset, GPIO15 pulse arguments and IRQ59/priority4 are instruction-bound. The older locked image now independently supports IOM6; physical wiring, measured timing, interrupt delivery and RF execution remain unknown. [Transport review](../coverage-audit-parallel-2026-10-09/TRANSPORT-INDEPENDENT-REVIEW.md).

**TDK belongs to an older calibration-patch lineage, not a uniquely identified SDK.** The SRAM callgraph is bound: `0x508E92 → 0x508FA6`, with register7C initial address/data transfer and register7E subsequent bytes. GAF setup writes the125-byte patch at `0x6D53D8` to SRAM `0xC80`, copies key at patch+8 and writes it to `0xB4`. All125 bytes exactly equal official1.0.7 and1.1.2, SHA `80eb396ba1b365d332aabebed514cccb19f5d5a8eba1d6543be61ceda4fa8b2f`. Official1.1.3/1.1.8 instead share a different189-byte patch and C5C/acceptance-offsetC layout. Independent calibration review passed12 checks. The selected stock insertion sequence has no1.1.8 unequal-ODR extra key write to50. [Calibration lineage review](../coverage-audit-parallel-2026-10-09/TDK-CALIBRATION-LAYOUT-INDEPENDENT-REVIEW.md).

The mounting writer `0x507710` sends18 bytes from the existing host Q14 cache to SRAM1AC. The cache is produced by the previously decoded nine-float Q14/Q30 transform; this does not establish the official int8 conversion wrapper. Public/stock callback ABI differences and mixed integration remain possible. Private EDMP/GAF ROM computation is not provided by host-source or patch-byte agreement. [Transport independent review](../tdk-transport-independent-review-2026-10-09/REPORT.md).

**Earlier TDK search correction:** the missed mounting entry was excluded by the hash-bound symbol filter: its only containing row was a huge hashless range, with no dedicated0x507710 row. The scanner accepted mov.w. The encoding was not the cause. Exact called-target decoding and newly hash-bound intervals close the transport/calibration mapping gaps; do not reopen them from the old negative-prefix/MOV results. Exact producing revision remains unresolved, because multiple official releases share the patch.

**BQ27427 uses a fixed-byte update, not Zephyr's selective sign clear.** Independent review reproduced17,752 initialized bytes and the seven-entry RAM table. Entry6 maps subclass105/block0/byte5/type1; stock sets the whole byte to28 and recomputes block checksum. Zephyr conditionally clears bit7 while preserving low seven bits. Twelve original update fixtures and an original commit/checksum fixture support the bounded software conclusion; reviewer independently recomputed checksumEC. Mode/transport/delay success stubs and synthetic valid/data state do not establish a physical write, calibration correctness or full configure round trip. The initialized-table mapping blocker is closed. [BQ independent review](../source-discovery-parallel-2026-10-09/BQ27427-DESCRIPTOR-INDEPENDENT-REVIEW.md).

**Flash has a conditional error-path ambiguity.** A nonzero RDCR transport error that returns normally can be treated as true by the mode predicate caller. Subsequent WRDI04 checks its own result, not mode readback; local routine may return0 after successful WRDI. Outer initialization discards the mode setter return before QE. Independent static review accepted this chain. Diagnostics may halt under unknown configuration; no physical fault is claimed. RDCR20 versus RDSCUR40 mask discrepancy remains withdrawn. [Flash review](../coverage-audit-parallel-2026-10-09/FLASH-ERROR-PATH-INDEPENDENT-REVIEW.md).

## Acquisitions, licenses and proposed references

| Reference | Outcome / license | Proposed handling |
|---|---|---|
| Official TDK ICM45608 history and1.1.8 | Root BSD-3-Clause; per-file notices retained. Historical1.0.7/1.1.2 patch is stock-byte equal;1.1.3/1.1.8 differs | Reuse registered TDK provider and retained historical comparators. Do not upgrade pin to1.1.8 based on newer availability; exact producer remains unproven |
| Official Zephyr BQ274xx driver at87a40fa6068d12d14a7a3521c3d12925da2cc37e | Apache-2.0 protocol/quirk reference; TI forum rationale could not be independently fetched | Keep isolated source reference; no claim stock source equals Zephyr and no automatic implementation change |
| TI-recommended Linux OPT3001 driver, pinned Linuxv6.6 | GPL-2.0-only; useful OPT3007-compatible protocol reference | Single-file reference proposal, not replacement firmware provider or proof of stock descriptor schema |
| Macronix MX25U25643G LLD1.1b | Proprietary internal use only; unauthorized distribution prohibited | Internal reference only; no public submodule/redistribution proposal |
| Goodix GR551x SDK utility carrier | BSD-3-Clause notice retained; newer46-row tables differ from historical43-row fingerprint | Negative comparator; does not establish Goodix fitted hardware or recover absent1.7.0 provider |
| Official QP/C6.5.1, ST HAL/CMSIS and already pinned Ambiq sources | Existing provider comparisons, not fresh matching whole-source discoveries; retain their recorded licenses/notices | Reuse existing provider evidence; no duplicate acquisition/registry changes |

All newly retained references are isolated under analysis acquisition directories with pinned provenance. No registration, gitlink, index, campaign admission or canonical-ledger update is part of this summary. Earlier [reviewed acquisition summary](../fresh-sdk-discovery-reviewed-successor-2026-10-09/SUMMARY.md) retains detailed negative comparisons and licensing boundaries.

## Bounded remaining questions

- Unique TDK host producer/compiler/configuration, other changed host functions/maps/patches and private ROM algorithms; full125-byte identity already closes the selected calibration question. A new discriminator needs an authenticated stock edge, not another broad history scan.
- Flash actual error reachability/diagnostic continuation, bus response and lane-phase contract; byte-normalized emulator traffic does not prove1/1/4 physical lanes or timeout margins.
- Physical BQ ROM calibration contents and fitted-board use; fixed28 behavior is proven only at software/static and bounded fixture levels.
- GX8002 CPU IRAM/DRAM visibility (DMA masking does not prove CPU aliasing), I2S maskbit8 enabling, vendor ARC LOG2 arithmetic/flags and authentic stock4.2 providers.
- Case producing build configuration and whole-image first-party P2 code/data reconstruction, review and freeze.

These are local evidence boundaries. This scan is not global source exhaustion, whole-firmware coverage, a byte-identical rebuild or hardware fidelity certification. Existing source-ledger work, seals and checkpoints are preserved.
