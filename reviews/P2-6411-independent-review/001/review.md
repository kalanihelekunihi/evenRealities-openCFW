# Independent review 6411

Disposition: **PASS_SCOPED**; `accepted:false`.

The packet hashes and E8A4..E8C2 source slice match. GNU Thumb decoding confirms an entry frame that saves R2/R3/R4/LR. It loads the caller's fifth stack argument from incoming SP+16 and writes it to the new SP0, replacing the saved-R2 slot and placing that argument where the indirect callee receives its fifth argument. It then freshly loads a literal-backed pointer at +4 and invokes it with the original R0-R3. Afterward, the wrapper performs three ordered literal-address stores (195, then zero, then zero) without changing the callee's R0. `POP {R1,R2,R4,PC}` consequently returns the fifth argument in R1, incoming R3 in R2, restores R4, and forwards the callee's R0.

This confirms instruction order and ABI slot effects, not the callback's purpose or the meaning of the stores. The adjacent bytes past E8C2 are outside the mapped extent. No canonical files or gates changed.
