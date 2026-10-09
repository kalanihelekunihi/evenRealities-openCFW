# Independent review 29957

**Result:** PASS_SCOPED; `accepted: false`.

Candidate: `/Users/kalani/Repo/evenRealities-openCFW/g2/build/pseudocode-first/20260930T190500Z/analysis/apollo-main-diagnostic-fixed-library-fresh-global-signed-gate-one-helper-frame8-return-30356-map/001`. Receipt and all five listed file hashes match. Independent reassembly confirms 48 locked bytes and 21 contiguous instructions over `[0x4EACC0,0x4EACF0)`.

The 8-byte `PUSH {R7,LR}` frame is modeled correctly. Literal `0x4EB744` is loaded into R1 and its pointee is separately read into R0; zero exits with R0=0. On the nonzero route, literal `0x4EB748` is loaded and its pointee freshly read; signed `BGE` continues only for a value at least 1. The code then freshly rereads the current R1 pointee and passes that result to opaque `44E498`. Its actual signed R0 result is thresholded at 1. The `POP {R1,PC}` loads a mutable saved slot into R1 and returns through the next slot while preserving the selected R0, subject to memory faults. No equality between repeated pointee reads or helper calls is assumed.

The result remains bounded and partial. Adjacent bytes are excluded and unclassified; helper semantics and global completeness are not established.
