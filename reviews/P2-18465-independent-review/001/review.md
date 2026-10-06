# Independent review P2-18465

Status: partial, unaccepted. No source or gate changes.

Fresh GNU ARM replay of the pinned image produced the exact 52-byte span `0x46015A..0x46018E`; instruction and PC-reference manifests match the candidate. The adapter at `0x46015A` saves R4-R6/LR and retains incoming R0-R2 in R4-R6. It issues calls `0x4411F2` then `0x441200`, resetting R2, R1, and R0 from those retained values before each call. R3 remains live (incoming for the first, previous child result for the second), and the second call's full R0 survives the POP return.

The initializer at `0x460178` checks the global through the PC-relative address `0x46061C`. A nonzero value returns as loaded. On zero, it sets R0 to zero and calls `0x44971C` with incoming R1-R3 still live; it stores the full returned R0 through the retained global address without reloading or checking it, then returns that child result. A zero child result therefore leaves the global zero and permits another initialization attempt. No synchronization or allocator contract is inferred.

No C, firmware-source, or gate changes were made, and no global coverage claim is made.
