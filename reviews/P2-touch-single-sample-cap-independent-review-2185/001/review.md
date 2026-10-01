# Independent review 2185: single-sample cap

**Result: PASS_SCOPED.** Candidate `analysis/touch-single-sample-cap-5c1e-2182/002` remains unaccepted.

The exact leaf computes its row and item addresses, reads validity at row+122 and split at row+58, and selects the secondary cap only when validity is one and slot is at least the split. It stores the cap only when the unsigned sample exceeds it. The wrapper bypasses the leaf for type 7 and returns the incoming index; otherwise the cap is the leaf’s incidental return.

All 324 isolated fixtures passed and matched frozen replay JSON; both bodies, source and artifacts hash-check and independent Thumb decoding matches. The corrected +58 offset is instruction-backed, but its allocation role is not established. Invalid indices, aliasing, concurrency and physical meaning remain open. No canonical records changed.
