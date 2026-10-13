# Complete supplied-bundle accounting and resource scan

All4301227bytes of locked s200_v2.2.6.10 EVENOTA are hash-authenticated and accounted in disjoint half-open intervals. Six payloads total4300283bytes;176byte outer header/TOC/trailer plus six128byte component headers account for944transport bytes. Existing container validator and six nonreflected CRC32Cchecks PASS. Exclusive component/bundle partitions have no holes or overlaps and independently sum exactly to original lengths. This is100%scan/accounting, not100%semantic understanding or code recovery.

## Exclusive evidence levels

Bundle totals:4660confirmed code,603459confirmed data,2743823suspected,949285unknown. Confirmed code is a deliberately narrow bound:88byte original-testedSMPtail plus4572bytes from seven hash-verified CASE task/callback CFG records(11disjoint spans). Suspected includes recognized function/envelope/compiled-candidate evidence and printable-string candidates; it is not proven code. The9164byte proprietary GXNPU command stream remains suspected accelerator code because its format is unresolved. Confirmed data includes validated image/resource structures, typed readonly/geometry tables, model weights, headers and encoded initializers. No zero/FF/entropy run is promoted to padding.

|Component|Payload bytes|Confirmed code|Confirmed data|Suspected|Unknown|
|---|---:|---:|---:|---:|---:|
|codec|326092|0|123120|110188|92784|
|ble_em9305|211948|0|1069|209395|1484|
|touch|34464|0|1188|28484|4792|
|case|55784|4572|6610|39720|4882|
|apollo_bootloader|148599|0|1897|127231|19471|
|apollo_main|3523396|88|468631|2228805|825872|

The original overlapping source/pseudocode/disassembly/compile/behavior/exact/integration stages are preserved separately. Data overlapping a function envelope does not erase earlier work.177conflict records retain resource/possible-code-or-string overlaps;0contradictory confirmed code/data claims. Exclusive confidence is based on stated parsing evidence; definitions do not expand from symbol counts.

## New high-impact resource findings

Full-offset scan of main with exact existing28byte LVGL9 L8schema finds431candidates:428pass magic/color/reserved/flags/geometry/size/pointer bounds;3reject. Previous map selected only six. All428pixel and428descriptor regions are labeled with addresses, dimensions,stride,format and exact original hashes; overlapping buffers deduplicate. Added evidence increases confirmed data419510unique bytes over the same scan before the wider descriptor search. These are raw grayscale raster arrays, not inferred PNG files or semantic icon names. Display/caller/hardware behavior remains unproved.

Additional existing tables now byte-bound:512byte TinyFrame CRC16/ARC table plus2272bytes of three DSP bit-reversal/Q15tables; seven LittleFS geometry fields(28bytes) independently match in main and bootloader. Existing37boot readonly items,203CASE strings, model weights and container metadata remain included. Embedded text is not called a standalone text file. Labels/contents summaries and type/provenance are recorded, without uploading pixels or firmware binaries.

PNG/sfnt/OpenType/gzip validators search all payload byte offsets for their declared signatures and check structural fields/checksums where applicable. No valid standard-format container is accepted. This is not proof of absent fonts/custom images or every file type.13317main plus other-component printable/NUL candidates are suspected only; sensitive-label previews are omitted.12canonical initialized/decoded images totaling795378bytes receive separate signature scans and hash checks; decoded offsets never inflate bundle totals. Supported signatures and rejection counts are recorded; universal format identification is not claimed.

## Flash versus decoded/RAM/external domains

Every bundle component has exact transport/payload translations and33canonical nested-image/source relationships. Codec overlapping banks, conditional load bases and UART images stay distinct; EM record target addresses are not invented physical flash capacity. Canonical virtual/load mappings are preserved; unbound wrapper/metadata offsets have no fabricated chip address.

Seven compressed initializer streams have exact encoded flash-source spans, decoded image hashes and validated prior transform receipts. Decoded ITCM/RAM can contain code,pointers,data and largezero regions; exact1:1byte backmapping is not invented. RAM-copy images/vectors are separate overlays. Heap configuration0x2F000has unknown base; WSF pool ranges, UI-registry leads and CASE task entrypoints remain RAM/runtime/code-domain evidence, not extra flash bytes or live-process snapshots. Task records identify entrypoints, not number of currently running tasks.

External MX25U25643G NOR is documented as32MiB with LittleFS[01400000,01FC0000),FlashDBsysenv[01FC0000,01FF8000),factory[01FF8000,02000000). These offsets are not contained in this OTA. Both internal LittleFS config tables validate read16/program256/block4096/count3008/cycles500/cache4096/lookahead256. No authenticated NOR contents are supplied; magic strings are not a mount, filesystem files or empty filesystem proof. A valid dump/geometry/state is prerequisite to metadata CRC/superblock/file traversal.

## Completed wave and publication boundary

Round362wave root-apollo-main-round362-layer-buffer completed2026-10-13T16:55:02.529094Z. Eight references verify. Two admitted bodies124+22native bytes,228bounded comparisons,54dependency hashes,3310definitions/761imports are retained as completed historical evidence. Object hash still matches; live source/dependency hashes have since drifted. Do not silently claim current-source rebuild coherence or automatic publication. Coordinator relay arrived; parent-mediated Page update/readback remains a separate step. Dataset records exact wave/hash/status and drift paths.

## Artifacts and validation

full-v3.json preserves raw accounting/evidence/conflicts,scans,RAM relationships,oldwork and wave. compact-v3.json is the full visualization view. compact-v3-packed.json is a192348byte lossless gzip/base64 transport with length-partition encoding; each component stage/exclusive run encodes[length,mask/class], start/end recover cumulatively from0. Bundle runs derive from component translations and metadata segments. Full raw ranges remain available. gzip decode and every restored interval exactly match original arrays; no downsampling. A modern-browser DecompressionStream(gzip) can decode it without external network assets; renderer capability still requires QA, not claimed here.

scan.py,package.py,transport.py and validate.py reproduce analysis and packing without firmware builds. Independent validate.py passes component/bundle closure,all resource hashes,33nested images,6CRCs and transport restoration. Tool identities/errors/rejected candidate counts and snapshot working-tree qualification are recorded. Only requested analysis outputs changed. No device actions,commits,branches,worktrees,dependency acquisition or denied provider work.

## Ranked bounded next goals

1. Extend typed custom-resource/table/font schema joins around the428L8descriptors; acceptance requires original-range/hash,valid record layout and explicit unknowns, not magic-only labels.
2. Resolve177resource-versus-envelope conflicts with existing CFG/literal-pool evidence; maintain exact exclusive sums and preserve both evidence layers.
3. Field/classification ownership for795378decoded RAM bytes, keeping compressed-source versus decoded coordinates separate.
4. Refresh round362source/object/dependency snapshot coherence and record successful parent publication/readback before calling automatic integration complete.
5. LittleFS metadata/files only after legitimate authenticated external-NOR content is supplied; validated superblock/CRC/state traversal then required. No restricted-phase retry/device writing is proposed.

## Export blocker

Library batch helper first failed during read-only hosted-tool discovery with DNS; no file upload began. The reviewed retry was rejected by automatic approval review: potentially sensitive firmware-analysis artifacts,unverified Library destination and no trusted user-authored authorization for this exact disclosure. The rejection explicitly prohibits workaround/indirect execution. No alternate upload route used; explicit approval request is pending. Therefore these v3files have no Library IDs yet; previously published v2identities remain unchanged. This is an export/authorization boundary,not an analysis or reconciliation failure.
