# Independent review 29991

**Result:** PASS_SCOPED; `accepted: false`.

Candidate: `/Users/kalani/Repo/evenRealities-openCFW/g2/build/pseudocode-first/20260930T190500Z/analysis/apollo-main-diagnostic-fixed-library-dispatch71-fresh-global-gates-frame48-return-30390-map/001`. Candidate hashes and locked image hash match its receipt. Independent reassembly confirms all 50 bytes in `[0x4EB180,0x4EB1B2)` decode contiguously as 21 Thumb instructions.

The selector-73 entry branches directly to the shared return sequence. The selector-71 path performs the documented ordered guards: fresh current-R6 word must equal one, fresh current-R5 word must be nonzero, a fresh literal into R5 and fresh pointee word must be nonzero, and the fresh byte at current R4+292 must be zero. It then freshly reads through current R5 for `44D878` and reloads through actual postcall R5 for `4EB7B8`. The one literal reference matches locked bytes. The shared return adds 28 to the actual SP and then pops five fresh words into R4/R5/R6/R7/PC, advancing SP by another 20; this skips the saved R3 slot and uses mutable saved values.

This is bounded partial evidence. No helper behavior, global coverage, source completeness, freeze, or byte equality is established.
