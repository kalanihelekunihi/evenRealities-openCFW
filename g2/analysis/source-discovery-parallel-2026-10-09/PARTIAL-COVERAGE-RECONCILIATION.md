# Partial artifact coverage reconciliation — 2026-10-09

Static parsing of existing authenticated images and historical raw corpora only. No build, decompiler run, canonical manifest edit or cancelled queue pass. All 10499 function **bounding-envelope** hashes freshly match their corresponding canonical image bytes; run image identities also match. Counts below union the declared inclusive Ghidra body ranges as half-open intervals, so overlapping functions/aliases count each byte once. Only decompiled=true records with existing corresponding `.c` exports enter the raw pseudocode union. No claim is made that those bytes are all code, that the pseudocode is correct or that all functions were discovered.

| Component | Image bytes | Envelope records | Ghidra body union bytes | Raw pseudocode artifact union bytes | decompiled=false | true but file missing |
|---|---:|---:|---:|---:|---:|---:|
| apollo-main | 3523364 | 8853 | 1628382 | 1555524 | 378 | 0 |
| apollo-bootloader | 148599 | 903 | 120432 | 112506 | 54 | 0 |
| touch | 34432 | 308 | 27879 | 27879 | 0 | 0 |
| case | 55752 | 435 | 43072 | 43072 | 0 | 0 |

The raw artifact union occupies44.1488%,75.7111%,80.9683%,77.2564% of these entire image byte denominators respectively. These are **image byte fractions associated with raw exports**, not semantic pseudocode completion percentages or fractions of known executable code. Header/data/resources in denominators remain unclassified; Ghidra ranges can include literals or mistaken boundaries. Envelope hashing authenticates bytes, not function interpretation. Export text manifests were previously audited by the P1 corpus audit, but this pass did not independently re-derive export text semantics.

`partial-artifact-range-unions.json` saves exact unions and complement intervals. Complement intervals number2768 main,255 bootloader,176 touch,296 case. These are gaps in this raw-export cohort, not missing-code counts; do not launch decompilation for them automatically. decompiled=false entries are retained in that JSON as missing_decompiled_artifacts; the table distinguishes unavailable exports from false decompilation flags.

## Trustworthy partial assembly mappings and limits

Existing EM9305 objdump RUN.json pins the complete official payload hash91a38f7fc05555f86181ecb22b363e3239bfcaaa2ff6171e98524ae64821eca9 and states range[0x302400,0x335BC8),210888bytes, matching record3's authenticated size. Exact runtime mapping still needs independently checked image-record address mapping; the filename/header is not sufficient to admit every listing line as instructions. The dump visibly decodes repeated words as branches and can include data. This is a bounded disassembly **candidate**, not210888bytes of validated assembly.

Existing codec full-xip.objdump.txt targets canonical binh_a_stage2_xip.bin (36484bytes SHA49c9aed0126493220a3e48827c267d5e94f64d51d9ede0ccc3e84b8946744584) at conditional runtime base0x10203004, end0x1020BE88. It uses disassembly of `.data`; visible literal words at0x10203008 are decoded as instructions. Thus whole-file listing availability cannot yield100% assembly semantics coverage. Previously bound mode/event function slices and reviewed descriptor word sites provide narrow instruction/data distinctions; they do not classify the whole image.

## Finite gaps for the audit track

1. Reconcile accepted, rejected, failed and superseded review IDs to each exact union interval before defining a reviewed-pseudocode numerator. Raw export flags alone are insufficient.
2. Classify the saved complement intervals into executable code, literal/data, padding, resources, container and unknown before deriving executable denominators. Never label complements as code by subtraction.
3. Resolve noncontiguous Ghidra body-ranges to actual instruction/data ranges; envelope hashes do not validate decoder semantics.
4. Map codec historical929 raw envelope records to canonical terminal images with alias normalization and authenticated hashes; exclude container parents and NPUweights from MCU instruction denominator. This pass provides no new codec-wide union.
5. Establish EM9305 record mapping and unique decoded instruction bytes, preserving failures/undecoded spans and excluding FHDR metadata. Raw ARC listing and targeted decompiler rounds have different scopes.
6. Separate raw instruction listing, semantically supported decoder output and authored build assembly; they are three different assembly metrics. Current evidence cannot support one blended assembly percentage.
7. R1 needs its own authenticated application/live bootloader/MBR/SoftDevice scopes and deduplicated corpus mapping. The four byte-array oracle entries are not a complete-chip executable denominator.

These are evidence reconciliation tasks, not authorizations to re-run broad decompilation or the cancelled queue. Existing raw corpora and new isolated JSON remain sufficient to reproduce the four partial Arm mappings.
