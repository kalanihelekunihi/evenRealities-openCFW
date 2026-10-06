# Independent review P2-18521

Status: partial, unaccepted. No source or gate changes.

Fresh GNU replay confirms the 104-byte span `0x460B68..0x460BD0`; instruction/reference manifests match. The first route uses fresh bit-0/conditional bit-2 reads. On its bit-2-set branch, R8 is reset to 52, lookup `0x460084` and then `0x45FFFE` run with the separately recomputed field pointer, and byte +40 then word +48 are freshly read into SP4/SP0. R8 is replaced by `low32(52*R7)` before the latter read, the selector is retained in R3, and `0x43CE9E` receives it.

The shared path at `0x460BBE` unconditionally sets R9=44, computes `R5 + 44*R7`, and reads word +8. Nonzero branches to the already mapped body at `0x46093A`; zero reaches excluded setup at `0x460BD0`. In the mapped body, R8 is reset to 52 before destination writes, so the diagnostic branch's R8 offset does not persist into that body. The source stride 44 and later +48 offset remain distinct literal arithmetic facts; no 52-stride reinterpretation is supported.

External continuation and alternative path remain incomplete; child contracts unresolved. Partial/unaccepted only.
