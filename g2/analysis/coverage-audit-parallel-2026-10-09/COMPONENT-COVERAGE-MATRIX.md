# Verified component coverage matrix — 2026-10-09

Current `g2/Makefile` reference target uses `g2/manifests/g2-2.2.6.10.json`. All six providers are official_blob. Independently checked each file's size/hash. **100% of payload bytes in that target are retained blobs:4,300,283/4,300,283.** Outer bundle adds944 container bytes to4,301,227. This is packaging, not source reconstruction. There is no proven complete source build for any of the six payloads(0/6 components). **A byte percentage fully compilable from integrated C remains unknown**, rather than0: focused source comparators and historical modules exist, but no admitted unique executable-byte map measures their integrated coverage.

| Component | Full payload bytes | Fully integrated C executable % | Default reference blob % | Raw pseudocode export: successful/recognized functions | Whole executable disassembly % |
|---|---:|---|---:|---|---|
| Apollo main |3,523,396|Unknown|100%|7,449/7,449=100%|Unknown|
| Apollo bootloader |148,599|Unknown|100%|849/903=94.02%|Unknown|
| Touch |34,464|Unknown|100%|308/308=100%|Unknown|
| Case |55,784|Unknown|100%|435/435=100%|Unknown|
| Codec |326,092|Unknown|100%|929/929=100% across five historical export images only|Unknown|
| EM9305 BLE |211,948|Unknown|100%|Unknown whole-component denominator; shard exports exist|Unknown|

Raw export function percentages are **availability of historical Ghidra output for recognized functions**, not fraction of all actual code, independently reviewed pseudocode, source compilability or correctness. The function JSONLs were independently checked against `g2/research/MANIFEST.sha256`; failed bootloader54 functions remain recorded. Corpus README expressly says this raw corpus is not reviewed pseudocode. No global weighted pseudocode/executable total is justified. There is also no code/data/padding partition complete enough to normalize these numbers to unique executable bytes. Body-byte sums are deliberately not added: overlap, literals and missed functions would distort the result.

Codec raw-export subdivisions: uart_stage1=32/32, uart_stage2=96/96, binh_a_stage2_xip=362/362, binh_a_stage2_sram=151/151, binh_b_stage2=288/288. Stage1 A/B programs and command/weight payloads are outside that929 denominator. Three consumed whole-image C-SKY/ARC dumps were independently hash-verified, supporting assembly availability for selected images; linear decoding mixed code/data is not100% executable disassembly or correctness.

## Complete canonical33-image inventory

Sizes below are image sizes, **not executable denominators**. Nested and initialized images overlap/derive from their parent; summing them double-counts source material. See COMPONENT-METRICS.json for parent IDs.

| Payload | Canonical images(size bytes) |
|---|---|
| Apollo main |flash3,523,364; decoded00000040=24; decoded20000000=17,752; decoded20080000=769,646|
| Apollo bootloader |flash148,599; decoded00000040=24; decoded20000000=1,371; decoded20080000=4,096|
| Touch |flash34,432; RAM vectors192; RAM initialized964|
| Case |flash55,752; decoded20000000=420|
| BLE EM9305 |records0/1/2/3=224/656/56/210,888; RAM initialized0/1/2=69/776/44|
| Codec |codec_payload326,092; uart_type1_container38,236; uart_stage1=10,240; uart_stage2=27,964; main_type2_container287,808; binh_a_stage1=12,288; binh_a_stage2_container51,200; binh_a_stage2_xip36,484; binh_a_stage2_sram14,716; binh_b_stage1=12,288; binh_b_stage2=82,060; npu_kws_command9,164; npu_kws_weights120,800|

Canonical `inventory/images.jsonl` contains33 images. Its70 coverage rows classify43 unknown spans and27 container spans; that G1 accounting is not a current P2 completion percentage. `workflow/state.json` still has G2–G6 not_run. Later local analyses do not turn this initial ledger into an executable coverage map automatically.

Touch's independently reviewed54/54 selected PDL functions covering4,952 full-extent bytes and runtime focused922 bytes are useful **selected exact comparator results**. They are not percentages of whole touch firmware, are not all pure C(includes compiler runtime/CRT assembly), include some data/alignment, and are not admitted whole-image integration. Historical core-source manifest records hybrid overlay providers and retained opaque bases; current default reference target does not use it, and changed/equivalent hybrid images do not satisfy the locked byte-identical target.

Evidence: `g2/Makefile`, `g2/manifests/g2-2.2.6.10.json`, `g2/manifests/g2-2.2.6.10-core-source.json`, `g2/workflow/state.json`, campaign `inventory/images.jsonl`/`coverage.jsonl`, `g2/research/README.md`, `g2/research/MANIFEST.sha256`; exact raw-export paths and independently verified numbers are in COMPONENT-METRICS.json. No builds, admissions, canonical changes, device access or source edits performed. Output only in this audit directory.

Cross-check against discovery COMPONENT-DENOMINATOR-AUDIT.md agrees on all six payload sizes,4,300,283total,33 images,blob providers and unknown executable percentages. Its Apollo-main historical envelope census8,853 is a different discovery population from the authenticated raw-export cohort7,449/7,449 here; neither is a true whole-code denominator. Historical source-overlay provider directories are absent and output pins differ from locked inputs, reinforcing exclusion of old source_owned percentages. No accepted P2 interval union was established by this bounded audit; canonical coverage and raw export counts alone cannot substitute for it.

## Bounded touch evidence and pending additions

Owner `touch-crt-array-binding-2026-10-09/COVERAGE-EVIDENCE.md` agrees with reviewed audit packets:

| Bounded group | Reviewed comparison extent | Meaning |
|---|---:|---|
| Selected PDL |54/54 functions;4,952 bytes|Selected finite census only|
| Additional I2C helpers |6 helpers;1,456 bytes|Outside selected54-function denominator|
| ProcessStatusCode |128 helper bytes+80 table bytes|Code/literals and switch-table data separately counted|
| Runtime providers |922 bytes|Compiler/newlib/CRT focused providers; includes assembly/alignment|
| New CRTbegin and array work |152 provider bytes+8 array data bytes|**Pending independent review; binary-provider attribution;0 claimed genuine crtstuff source-rebuilt bytes**|

Owner reports reviewed group arithmetic4,952+1,456+208+922=7,538 full comparison bytes. This is a useful bounded evidence count, not an admitted component source percentage; this matrix does not claim a newly reconciled global interval union from that arithmetic. Prior reviews establish those individual groups and their explicit local bounds. The pending160 bytes are excluded from reviewed/source-produced totals. Current workflow has zero C implementation assignments; local C comparators remain separate from campaign implementation readiness.

## Raw assembly availability and pseudocode output checks

Successful pseudocode numerators above mean actual `decompiled:true` records **and nonempty generated function bodies**, not merely created files. Independently checked each successful per-function C export for braces/nonempty content; main has7,449 nonempty function records across16 bundles. All those output files match the research manifest. This verifies recorded decompiler success/output availability, not semantic correctness. Bootloader54 failed rows are excluded.

| Component | Defensible raw assembly availability verified here |
|---|---|
| Codec |2 image-specific whole-image exports: binh_a_stage2_xip and binh_a_stage2_sram |
| EM9305 |1 record-3 application export(0x302400–0x335BC8) |
| Apollo main / bootloader / touch / case |Unknown aggregate; local instruction evidence exists, but no complete export registry was audited |

These are minimum known image-export counts, **not**2/33 or1/33 code coverage, and do not claim missing exports elsewhere. The three dumps' hashes are verified in COMPONENT-METRICS.json. Function-disassembly percentages require an authoritative discovered-function list linked to every exported instruction range with statuses and overlap/alias handling. Executable-byte percentages additionally need authenticated code/data/padding classification, address-to-image conversion and unique span unions for all33 images(including initialized/decoded aliases). Those mappings are not furnished by the current canonical70-row ledger or the three dump-presence receipts. Consequently no raw assembly percentage or global executable total is claimed.

Later additive status: CRT-BINDING-REVIEW.md now independently passes the152-byte binary-provider attribution and separate8-byte copy-bound array data. Their previous pending status is superseded **only for attribution**; genuine crtstuff source-produced coverage remains0, and reviewed runtime source subtotal remains922. No requested component percentage changes.

Later additive raw-byte metric: PARTIAL-UNION-REVIEW.md independently verifies all10,499 Arm envelope hashes and exact successful-export interval unions. Whole-payload artifact-associated fractions are Apollo main1,555,524/3,523,396=44.148430%; bootloader112,506/148,599=75.711142%; touch27,879/34,464=80.893106%; case43,072/55,784=77.212104%. These are **raw-export-associated byte fractions**, not executable/semantic/source completion. New main cohort is8,475successful/8,853 recognized, separate from earlier7,449/7,449 harvest. Codec/BLE union percentages remain unknown and no global weighted total is justified.

Later codec/EM additive artifact metrics independently pass CODEC-LISTING-REVIEW.md: codec raw-export union92,560/326,092=28.384628%; codec XIP byte-matched listing36,484/326,092=11.188254%; EM listing210,072/211,948=99.114877%. EMrecord3gap816 plus1060other-record/metadata bytes equals1876unrepresented payload bytes. Corrected C-SKY serialization has zero mismatches; failed3775-line receipt is preserved and independently reproduced. These are artifact representation fractions, not executable/reviewed/semantic assembly or source coverage. EM pseudocode remains unknown.

Later source upgrade: CRT-SOURCE-REVIEW.md now passes genuine pinned CRT source/configuration generation and exact source link. Existing152binary-attributed bytes become source-produced; no new unique binary bytes. Runtime focused source subtotal1074(922+152), separate8array-data bytes and4CRT_ENDterminator-data bytes. This supersedes the prior binary-only/source0status for that packet, without establishing whole-component C percentage or full object identity.
