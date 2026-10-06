# Independent review P2-18463

Status: partial, unaccepted. No source or gate changes.

Fresh GNU ARM replay of the pinned image produced the exact 50-byte interval `0x460128..0x46015A`; the instruction and PC-reference manifests match the candidate. The map correctly describes a 16-byte saved-register frame retaining incoming R0/R1/R2 in R4/R5/R6, followed by four calls in order: `0x44122A`, `0x441238`, `0x44120E`, `0x44121C`. Before each call, the adapter resets R2 from retained R6, R1 from retained R5, and R0 from retained R4. R3 remains live across the adapter and can therefore carry the incoming value on the first call and a prior child result later. The first three child R0 values are overwritten by the next argument setup; the fourth R0 remains the function result through POP of R4-R6 and PC.

All child semantics remain unresolved. Similarity to another call sequence does not establish address aliasing or function identity. This is a local map review only.
