# Address-based coverage: verified bounded sample

Address-coordinate coverage is useful, provided stages stay orthogonal. This sample uses official s200_v2.2.6.10 image identities, half-open ranges, and deduplicated unions. measure.py reproduces measurements using existing artifacts only; inputs_sha256 in results.json records actual consumed file identities. No firmware build, denied phase, canonical/index/other-source changes.

## What the tables define

Reference memory-map.md defines physical/virtual memory regions, firmware placement and storage partitions. FlashDB kvdb[01FC0000,01FF8000)224KiB and NVdb[01FF8000,02000000)32KiB are database storage partitions, not C-module boundaries or the main-code denominator. Main OTA strips32byte preamble before flash438000. CASE strips32byte EVEN header before08000000. EM nested records have independent address identity; selected envelopes here lie within record3[302400,335BC8). Never combine overlapping decoded/RAM/parent image aliases by address alone.

A function ownership table can infer software groupings inside an image, but does not prove module ownership, code-only boundaries or a complete instruction inventory. Classification must distinguish instruction, literal/data, padding, unknown and unmapped rather than labeling every function envelope 'code'. This sample leaves exhaustive classifications unknown.

## Actual measured module samples

| Image/module sample | Rows/functions | Deduplicated stock envelope bytes | Mapped C | Compile evidence | Behavior evidence | Exact byte match | Integrated replacement |
|---|---:|---:|---|---|---|---|---|
| Main TLSF four public entries |4|376|Matched upstream C comparator|All4 compile in retained comparator|Selected74operation sequences, arena/provider-qualified prior independent review|0/4bodies;0bytes|0bytes|
| EM candidate envelope collection |241|15190|Declared recreated-C static correspondences|Unknown across this whole union without per-body selected-object receipt join|Unknown across this union|Unknown|0reference replacement bytes|
| CASE function attribution table |435rows;428positive extents|40664|Ownership categories only; not authenticated C body coverage|Unknown from table|Unknown from table|Unknown from table|0reference replacement bytes|

TLSF subcomponents: tlsf_create_with_pool[0x4d06ec,0x4d0716) 42bytes; tlsf_malloc[0x4d0722,0x4d0744) 34bytes; tlsf_free[0x4d0808,0x4d0852) 74bytes; tlsf_realloc[0x4d0868,0x4d094a) 226bytes. Each raw slice hash is verified against locked main. Candidate has complete upstream C source with test/runtime dependencies; no inferred coverage of all helper bodies.376/376is100%of this explicitly selected sample, not100%TLSF or main. Source output sizes96/50/292/444 differ from originals. Assembly/data provenance is not mixed into C.

EM static grouping by declared source labels: controller_init.c183envelopes/10766uniquebytes; controller_timer_helpers.c13/992; sleep outer/controller/mode1/516; sleep metadata/prepare1/316. Remaining groups/ranges in results.json. These are inferred source subcomponents, not flash-partition-defined modules. Important correction: declared sum15210 minus20overlap equals15190uniquebytes. This is7.16685%of211948payload bytes as static mapping extent only; it is not compiled-C percentage or a reviewed executable denominator. The receipt itself disclaims semantic/equality/full-image completion; not all recently added source envelopes necessarily appear here.

CASE attribution groups: CMSIS/startup15positive rows/310bytes; FreeRTOS86/5814; STM32HAL15/1324; first-party90/18330; unresolved222/14886. Group sums40664equal unique total for this table.435rows include7zero-size named task entries deliberately excluded to prevent overlap with separately bounded CFG/task accounting. They are unresolved by this table's byte measure, not absent source functions. Mapping covers428/435positive table rows and40664/55784=72.89545%of stored payload as attribution-envelope representation. Remaining15120payload bytes include header/data/padding and unmapped material; they are not proven missing executable code or binary-only. Table category first_party_g2 does not mean recreated C exists, and upstream labels do not mean source compilation.

## Other available bounded evidence

Touch's three PDL complete source sections424+48+160=632bytes are prior-reviewed exact upstream-C matches, not newly recreated C or complete touch layout. Codec nine selected exact DSP sections1606bytes are source assembly, not C. Compiling candidate graphs for six architectures and object/provider counts remain independent from these address measures. No table permits summing upstream C, recreated C, assembly, pseudocode and data into one coverage percentage.

Pseudocode/assembly totals remain separately in component-percentages-2026-10-10/REPORT.md with explicit payload versus discovered-function denominators. This sample does not join every per-function artifact to each module; consequently module pseudocode/disassembly stage totals remain unknown unless a range+hash join supplies them. This is not zero coverage. Current reference package has4300283/4300283original payload bytes; actual integrated replacement0. The generated candidate relocatables are not source replacements in that package.

## Exact requirements for a reliable full inventory

1. Authenticate each image/version and decode parent/child/RAM coordinate mapping; use stable image IDs plus half-open intervals. Keep metadata/wrapper/data/unknown spans separate and define reviewed executable denominator before code percentages.
2. Join every module/function attribution to original range/hash, source path/hash and origin category (recreated/upstream/assembly/generated data), selected compile object/hash/command and full section/relocation identity. Names/comments alone remain leads.
3. Independently attach behavior receipts with tested branches/providers/runtime scope, exact-byte receipts including relocation/placement, and integrated absolute-image composition receipts proving actual replacement. Preserve stage overlaps; do not add stage percentages.
4. Join raw pseudocode/export/listing hashes and intervals, deduplicate within image/module and explicitly account shared functions/multi-module ownership. Reject zero-size/inferred-gap boundaries as code extents until independently established.
5. Snapshot concurrent source/receipt hashes. Produce global interval union only after all-stage joins; unknown remainder cannot be called binary-only. Packaging composition is independently measurable now and stays100%blob until actual image manifests replace bytes.

This is a verified sample and reproducible measurement, not a complete six-image semantic module inventory. Remaining work is evidence joining/classification, not more arbitrary linear disassembly or compilation merely to raise object counts. Useful actionable finding: reconcile the EM20byte overlap before repeating its15210byte subtotal as unique coverage.

Evidence: g2/docs/reference/memory-map.md; g2/tools/manifests/g2-box-function-map.tsv; g2/analysis/c-source-completion-20261011/em9305/body-coverage-boundary.json; g2/analysis/tlsf-main-source-comparison-20261010-implementation/byte-comparison.json; independent tlsf-execution-review-2026-10-10 and touch-compiler14 reports. Artifact hashes and detailed ranges are in results.json.
