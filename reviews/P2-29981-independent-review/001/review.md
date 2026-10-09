# Independent review 29981

**Result:** PASS_SCOPED; `accepted: false`.

Candidate: `/Users/kalani/Repo/evenRealities-openCFW/g2/build/pseudocode-first/20260930T190500Z/analysis/apollo-main-diagnostic-fixed-library-fresh-stack-byte-event755-six-value-dispatch-frame48-middle-30380-map/001`. Candidate file hashes and the locked image hash match its receipt. Independent reassembly verifies all 114 bytes in `[0x4EAFD8,0x4EB04A)` as 42 contiguous Thumb instructions.

The incoming byte is freshly loaded from `SP+12` into R7. Separate query calls gate event755 through bit1 and the following diagnostic through bit0 or bit2. The event arguments are assembled from low-byte R7, fresh words and the stated current stack slots. `MOVS.W R0,#0x0C400000` yields N=Z=C=0 and preserves V. After the diagnostic path, the code explicitly truncates the then-current R7 to eight bits and dispatches values 10, 68, 69, 71, 72, and 73 to their decoded targets, with all other values taking the default target. No helper register preservation is assumed.

This is bounded partial evidence. Every dispatch continuation lies beyond this interval; no helper behavior, global coverage, source completeness, freeze, or byte equality is established.
