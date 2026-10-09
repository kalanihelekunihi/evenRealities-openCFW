# Component/build denominator audit — 2026-10-09

Read-only inspection; no build, admission or cancelled queue execution. Supporting input hashes, complete image records, provider pins and legacy accounting are saved in `component-denominator-evidence.json`.

## Locked G2 payload denominators

| Component | Original payload bytes | Regions |
|---|---:|---|
| codec | 326092 | fwpk_metadata: 48, codec_stage_1: 38236, codec_stage_2: 287808 |
| ble_em9305 | 211948 | record_metadata: 124, record_0: 224, record_1: 656, record_2_fhdr: 56, record_3_application: 210888 |
| touch | 34464 | fwpk_wrapper: 32, touch_application: 34432 |
| case | 55784 | even_wrapper: 32, case_application: 55752 |
| apollo_bootloader | 148599 | apollo_bootloader: 148599 |
| apollo_main | 3523396 | ota_preamble: 32, apollo_main_application: 3523364 |

Six payloads total 4,300,283 bytes; locked EVENOTA is 4,301,227 bytes, leaving 944 package-level bytes. These are **artifact** denominators, not executable-code denominators. Model weights, resources, wrappers, literals and executable instructions must not be conflated.

`g2/Makefile:71` reference target invokes open_cfw.py against `manifests/g2-2.2.6.10.json`. All six providers are `official_blob`; `open_cfw.py:563–621` reads and hashes existing provider files. It does not compile firmware. Thus the presently selected reference-packaging path consumes all 4,300,283 original payload bytes as blobs (100% per payload); this is input dependency, **not** a claim that none of the firmware has reconstructed C elsewhere. Complete blob-independent C build success is unestablished for every component.

The historical core-source manifest extends the reference manifest; only bootloader, main and EM9305 replace providers with `source_build`. Codec merely overrides regions, so codec/touch/case still inherit official_blob. Historical build directories `components/bootloader/core_overlay`, `components/apollo_main/core_overlay`, `components/em9305/source_overlay` are absent; these manifest labels cannot establish current compilability. Their output pins differ from locked official pins and output sizes are respectively 163840,3956672,212984 rather than 148599,3523396,211948.

Historical bootloader accounting: source_owned65715, opaque81279, generated_patch_site16830, alignment16, sum163840. Historical EM9305: source_owned1174, opaque210584, generated_patch_site1102, container124, sum212984. These are old **output** counts; source_owned does not mean entirely C (can include assembly/patch machinery), and dividing by original payload sizes is invalid. Main provider lacks comparable source/opaque counts. Do not present these as present completion percentages.

## Image inclusion rules

`inventory/images.jsonl` currently lists33 image records. Top-level executable-image candidates: main3523364; bootloader148599; touch34432; case55752; EM9305 records224+656+56+210888=211824. EM record2 FHDR56 is metadata, not executable coverage. Codec nesting includes containers326092/38236/287808/51200 and children; never sum parents and children. Codec terminal raw candidates: UART10240+27964, imageA12288+36484+14716, imageB12288+82060, NPU command9164 and weights120800. Terminal bytes sum326004; remaining88 wrapper/container bytes. NPU commands are accelerator instruction/model data, separate from MCU C/assembly. SRAM/data boundaries are not all settled. Decoded initialized images can duplicate or expand flash representation; do not add them to package byte denominator.

Current coverage.jsonl contains70 interval records:43 unknown and27 container, with pending-admission qualifications. This inventory is not an up-to-date accepted-pseudocode or assembly progress ledger; **do not report 0% from this alone**, nor100% from text file existence. Audit track must reconcile accepted reviewed routine intervals and their unions to executable image scope, preserving failed/rejected/superseded receipts. Assembly coverage should distinguish raw disassembly, instruction-backed classification, semantically supported decode and authored build assembly.

Raw historical authenticated Arm envelope census in inventory/status.json: Apollo main8853, bootloader903, touch308, case435 =10499 function envelopes. Codec historical corpus929 envelopes across five inputs. These are discovery/corpus counts, not complete true-function denominators and not reviewed-pseudocode numerators; overlap, split entries, literals and aliases require union/deduplication. No safe C/pseudocode/assembly percentages follow directly.

## R1 oracle boundary

R1 Makefile distinguishes structural corpus checks from its exact-byte oracle. `research/decompilation/rebuild/Makefile:8` compiles emit_image.c with required application.bytes.inc, bootloader.bytes.inc, uicr.bytes.inc and approtect-runtime.bytes.inc. These byte arrays retain official images; compiling the emitter is not rebuilding firmware C. Manifest application646408; bootloader24576; UICR776; approtect-runtime12. Their total671772 is the oracle cohort, not a complete chip flash denominator. UICR is configuration, approtect runtime12 is separate small code cohort; bootloader/application provenance mixes release and live snapshot, so do not merge it into one official package. SoftDevice/MBR coverage is outside these four oracle entries. All four emitted oracle artifacts depend on their full byte arrays.

## Remaining limits

Delivering source completeness percentages requires a current immutable source-to-output span map with language classification, existing compiler/link inputs and accepted validation receipts. Pseudocode and assembly percentages need separately defined routine or byte denominators and current accepted interval unions. Neither stale overlay accounting nor upstream source availability supplies that evidence. No root/canonical edits or new task execution occurred.
