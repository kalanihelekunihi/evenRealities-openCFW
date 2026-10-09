# Independent review 30011

**Result:** PASS_SCOPED; `accepted: false`.

Candidate: `/Users/kalani/Repo/evenRealities-openCFW/g2/build/pseudocode-first/20260930T190500Z/analysis/apollo-main-diagnostic-fixed-library-six-byte-inputten-packet-input72-gate-frame40-middle-30410-map/001`. Candidate hashes and the locked image hash match the receipt. Independent reassembly confirms `[0x4EB398,0x4EB3D6)` contains 62 contiguous bytes and 27 Thumb instructions.

The first entry constructs a six-byte packet at the current `SP+24`: bytes `[0,10,0,0,0,0]`, then passes R3=0, R2=6, R1=current `SP+24`, and R0=1 to `464BB2`. After return, control branches to the external `0x4EB490`; no result assumption is made. A separate entry compares its incoming R0 against 72. On equality it loads the fresh `4EB740` pointer and reads byte+292; zero branches outside to `0x4EB3D6`, while nonzero sets R0=0 and branches to `0x4EB490`. The literal reference matches the locked image, and address formation/store semantics are consistent with the listing.

This is bounded partial evidence. The listed destinations are outside the interval; packet behavior and helper contracts are not inferred. No global coverage, source completeness, freeze, or byte equality is established.
