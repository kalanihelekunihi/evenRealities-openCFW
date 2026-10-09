# Independent source-discovery static review

The initial STATIC-COMPARISON is useful bounded lead generation. Target identity and acquired-source integrity are verified; exact source attribution, live VAD execution and unique producing branch remain unproven. No downloaded code was run.

[DISCOVERY-VERIFICATION.json](DISCOVERY-VERIFICATION.json) independently recomputes all thirteen official codec slices from their recorded payload offsets/sizes: all stock hashes match. It also checks all 2,970 embARC and 580 AIoT acquired-file hashes against provenance: no mismatches. Read-only Git HEAD and origin queries agree with the exact reported commits and URLs. This confirms the local records and checkouts, not an independent fresh network verification of current remote reachability.

Raw VAD/board-string occurrence lists independently match all recorded payload offsets, including both copies. These are package offsets, not virtual addresses or executable references. The candidate names remain inferred symbol leads; hashing target slices does not validate names, opcode lineage or source-to-target correspondence.

## VAD discrimination strength

Existing KWS `lvp/common/lvp_audio_in.c` has actual printf calls for VAD parameters 3/2/1 at lines 668/699/730. Acquired AIoT has those lines commented at 653/684/715. Thus these specific unmodified AIoT source lines cannot emit those literal arguments through their own compilation. KWS is a better direct explanation of this diagnostic-text lineage.

However, the report's phrase “active VAD format-string evidence” should be read as “present VAD diagnostic strings.” Neither presence nor two embedded copies proves reachable execution. A linked dead section, a prebuilt archive from a different lineage, retained data copied from a prior build, another object containing identical strings, another revision, or private modifications can explain them. Link retention alone cannot resurrect commented-out text from a freshly compiled translation unit, but can retain another object/archive that already contains it. These alternatives prevent exclusion of AIoT-derived whole-program lineage.

Executable xrefs would improve attribution: bind each string's containing child/image, identify an actual literal/address load and reachable printf caller, and compare that function's conditional branches and thresholds against both pinned sources. Static xrefs still would not establish runtime execution. Compare only new discriminating paths and preserve existing source/function admissions. Absence of `[MSG2.0]` is weak negative evidence because logging configuration, optimization and link elimination may suppress it.

## Provenance and licensing

The local origin URLs and revisions support the claimed source acquisitions. AIoT root LICENSE is MIT, copyright NationalChip 2024; its vectors.S explicitly carries Apache-2.0. This confirms the report's qualification that root terms cannot be applied indiscriminately to every bundled component. embARC root-license attribution was included in its verified file manifest; this audit did not perform a legal review of all component notices. Any imported source must retain its own notices and binary archives must not be described as source.

The 25 comment/whitespace-only classifications are explicitly heuristic, so the 43 remaining differences are candidates rather than 43 meaningful semantic changes. The inspected UART/VAD source distinction supports the report's correction that UART is shared-family evidence and VAD is a differential lead. New checkouts do not establish added recovered firmware bytes or source completeness.

## Extended comparisons

At this review snapshot only STATIC-COMPARISON.md was present under the comparison-report naming search. Forthcoming extended claims have not been reviewed and must not inherit this assessment. For each new claimed discriminator require exact two-source pins/hashes, configuration conditions, authenticated target region and byte/semantic correspondence; account for dead-code, archive and private-change alternatives.

This audit stayed within repository files, changed only this audit directory, performed only read-only Git metadata queries, and ran no downloaded code, compilation, device access or denied-path retry.
