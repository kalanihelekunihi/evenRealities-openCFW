# Independent review 30013

**Result:** PASS_SCOPED; `accepted: false`.

Candidate: `/Users/kalani/Repo/evenRealities-openCFW/g2/build/pseudocode-first/20260930T190500Z/analysis/apollo-main-diagnostic-fixed-library-six-byte-input72-packet-input69-gate-frame40-middle-30412-map/001`. Candidate hashes and locked image hash match the receipt. Independent reassembly confirms 66 contiguous bytes and 29 Thumb instructions in `[0x4EB3D6,0x4EB418)`.

The packet construction writes `[0,72,0,0,0,0]` at current `SP+16`, then passes R3=0, R2=6, R1=current `SP+16`, R0=1 to `464BB2`. The separate entry compares incoming R0 with 73 and branches directly outside on equality; otherwise it compares with 69 and branches elsewhere on mismatch. The 69 path freshly loads the `4EB740` pointer, tests byte+292, branches outside when zero, and otherwise sets R0=0 before an external branch. All pointer loads and stack addresses align with the decoded instructions.

This is bounded partial evidence. All continuations are excluded; packet/helper behavior and broader coverage are not inferred. No source completeness, freeze, or byte equality is established.
