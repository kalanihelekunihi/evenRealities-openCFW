# G2 component audit — 2026-10-07T22:51:03.475562+00:00

The completed selector23 operation has no pending receipts. This audit performs read-only measurement; it does not rebuild, generate firmware, edit campaign state, stage, commit or touch hardware.

**Complete source-buildable payloads:0/6 (0%). Byte-identical source-built payloads:0/6 (0%); byte-identical source-built bundles:0/1 (0%).** All six current production providers are official_blob, so100% of each stored payload is pulled from its official binary. That is whole-payload build dependence, not a claim that100% of its executable code is unreconstructed. Known non-code resources must be separated from executable blobs.

Official bundle:4,301,227 bytes, SHA-256f4dfb0b49ad3de3c2daf17f8a27a157c3dc98411d6a0d3ab2cfd0918f41b9afa. Six payloads total4,300,283 bytes; container overhead is944 bytes. Every payload identity is freshly reauthenticated. The matched reference package is blob-based and is not evidence of a source-built image.

## Whole-payload byte footprints

Every percentage below divides by the full stored payload size, including non-code and unknown bytes. These are unioned addressed bytes, not numbers of files, tests or text characters. A full executable denominator does not exist, so code-only and exact source-replacement percentages are **not measured** for every payload.

|Payload|Stored bytes|Assembly/export footprint|Generated decompiler pseudocode|Scoped reviewed pseudocode|Compared compiled-C slice footprint|Production binary pull-through|
|---|---:|---:|---:|---:|---:|---:|
|Apollo main|3,523,396|532,294 (15.11%)|1,626,380 (46.16%)|60,284 (1.71%)|8,184 (0.23%)|100%|
|Apollo bootloader|148,599|123,960 (83.42%)|112,506 (75.71%)|101,936 (68.60%)|67,740 (45.59%)|100%|
|EM9305 BLE|211,948|208,840 (98.53%)|0 (0.00%)|1,530 (0.72%)|0 (0.00%)|100%|
|GX codec|326,092|not measured|92,560 (28.38%)|2,170 (0.67%)|0 (0.00%)|100%|
|Touch|34,464|not measured|27,879 (80.89%)|15,926 (46.21%)|234 (0.68%)|100%|
|Case|55,784|41,082 (73.64%)|43,072 (77.21%)|22,814 (40.90%)|0 (0.00%)|100%|

Generated pseudocode is the existing hash-pinned decompiler catalogue/export footprint. Reviewed coverage uses the same authenticated scoped-review parser as the prior audit; it includes handwritten ARC/codec analyses outside that generated catalogue, hence EM9305 can have reviewed bytes while generated decompiler coverage is0. Scoped reviews retain their prefix/stub/static limitations and are not all-path semantic completion. Assembly footprints authenticate decoder/export bytes, not an exhaustive code/data partition; a linear ARC decode can also interpret data. Missing codec/touch assembly census means unmeasured, not absent analysis.

The compiled-C column measures original instruction bytes exercised in comparisons involving linked C slices. It includes inherited synthetic MMIO, ROM/providers and explicitly controlled boundaries. It **does not certify every body, source completeness or a functional source-rebuilt payload**. Zero means no admitted evidence in this census, not proof that no standalone C exists. For the bootloader, a stricter independently byte-mapped subset is nine compiler-installed PCM bodies totaling2,656 bytes (1.79% of stored payload); this is an auditable lower bound, not the entire source map. Exact residual opaque executable bytes cannot be computed as100%-C or100%-pseudocode.

## Current conservative code/data partition

This table reauthenticates the bounded Oct5 non-code map and adds exact authenticated executed-byte evidence from current successful comparisons. Executable counts are lower bounds. Every other byte remains unclassified, including many known candidate function ranges and compressed/runtime data not yet admitted by this conservative classification method. A0 lower bound is not a claim that a payload contains no code.

|Payload|Observed/confirmed executable lower bound|Confirmed non-code|Metadata/padding|Unclassified|Exhaustive executable denominator|
|---|---:|---:|---:|---:|---|
|Apollo main|9,706|29,064|0|3,484,626|not measured|
|Apollo bootloader|67,740|64|0|80,795|not measured|
|EM9305 BLE|0|40|124|211,784|not measured|
|GX codec|0|122,343|148|203,601|not measured|
|Touch|234|196|32|34,002|not measured|
|Case|0|64|32|55,688|not measured|

Confirmed non-code totals151,771 payload bytes. The fresh audit adds the64-byte Apollo bootloader core exception-vector prefix: documented/native VTOR410000 and authenticated little-endian stack/Thumb-handler words; it does not claim the entire external-interrupt table is mapped. Codec contributes122,343 bytes, principally typed model data/vector/control structures; Apollo main contributes29,064 consumer-attributed image storage/descriptors and pointer literals. Besides that64-byte bootloader prefix, the remaining300 bytes are confirmed touch/case/EM structures. These are resources/metadata, not executable-source debts. Whether every retained resource can legally/practically ship is outside this reconstruction metric. Compressed initialization/runtime expansions are not added to stored byte totals.

The frozen input census records five legacy receipt-file hash conflicts: four files in case-buffered-receive-handler-678/001 and touch-acquisition-budget-7288-1544/001/replay.py. They are disclosed in input-conflicts.json; the former pseudocode is not hash-bound by the current parser, and replay-text differences are not promoted to new executable/source coverage.

Twenty-four trace rows fail direct locked-byte matching and are excluded (for example mutated integration-fixture instructions at43004a); trace-inputs.json records them. Counts never include those mismatches or double-count overlapping tests. The classification sum reconciles exactly to each payload. A static disassembly footprint is not silently promoted into confirmed executable bytes.

## Comparable change since2026-10-06 13:20 UTC

|Metric|Prior|Current|Change|
|---|---:|---:|---:|
|Assembly/export footprint|599,718|906,176|+306,458|
|Generated decompiler pseudocode|1,902,397|1,902,397|+0|
|Scoped reviewed pseudocode|204,660|204,660|+0|
|Compared compiled-C slice footprint|8,418|76,158|+67,740|

Generated and scoped-review catalogue footprints are unchanged. Assembly gains306,458 Apollo-main bytes in the comparable receipt-pinned measurement. Compiled slice-footprint gains67,740 bootloader bytes because this audit now admits completed bootloader evidence; that is not a claim that all67,740 bytes were newly implemented since the prior scan. Main8,184 and touch234 byte compiled-trace footprints are unchanged. Broader ad-hoc knowledge work may exist outside the supported corpus schemas and remains uncounted rather than inferred.

## Core subcomponents and build limits

|Area|Concrete current evidence|Whole-area completion denominator|
|---|---|---|
|Bootloader startup/storage/kernel/peripherals|223-object8aca98ea offline image; seven exact-image cases pass; frozen-object relink and two new C-object reproductions pass. Root/reset/task callbacks have explicit contracts/models.|not measured|
|PCM power transitions|Nine individually mapped compiler-installed bodies2,656 bytes; selector23 all200 bytes/241 direct comparisons; natural8↔12 chains, raw-return handling and completion ownership evidence. Selector10 reuse is test-only and remains unbound; slots4/7/9/10/13/19 unsupported.|not measured for whole power subsystem|
|Apollo main RTOS/GPIO/buses/audio/IPC|8,184 byte admitted compared-C footprint across foundation slices. Hardware DMA/cache coherency, full scheduler/context and complete BLE/app transport remain outside these bounded fixtures.|not measured|
|Touch control|234 byte admitted compared-C footprint; complete controller image not rebuilt from source.|not measured|
|EM9305/GX/case|Authenticated instruction/pseudocode/review work and source/provenance hypotheses; record packaging or SDK archive matching is not an executable source replacement.|not measured|

The build configuration still reads all six official providers through open_cfw.read_providers. The EM9305 source-image builder packages supplied record programs; it does not synthesize the vendor/controller executable programs. Standalone C objects, component ELFs and synthetic simulators are useful progress, but do not increase the count of completely source-buildable payloads. Reconstructed target bodies plus external resident ROM APIs also require explicit dependence accounting.

## Reproduction and frozen snapshot

components.csv contains numerators, whole-payload percentages, null/unmeasured fields, per-payload deltas and build status. snapshot.json records this measurement time and authenticated identities; input-manifest.json binds selected inputs/build providers. Detailed byte unions, raw/review/export ledgers, method scripts and frozen-input-files.jsonl are in g2/build/audits/component-audit-2026-10-07T223956Z/. Only these newly generated audit ledgers were relocated from the report directory; project source evidence was not moved.

Measurement methods reproduce the prior scan:measure.py inventories current corpus; review_repair.repair applies the same corrected review binding; instruction_measure.py matches receipt-pinned instruction bytes plus authenticated ARC text; bundle_metrics.py projects identity transforms. aggregate.py combines verified byte unions and providers. Source-replacement and opaque-executable denominators remain null deliberately. Fresh reruns can advance if other agents write evidence; the frozen input-file manifest, output hashes and byte ledgers define this snapshot.

No complete functional source-rebuilt hardware image or official byte-identical source build is demonstrated. The next measurement gap is an exhaustive nonoverlapping executable/data partition and source-to-original body ownership ledger tied to a complete build, not additional file counts.
