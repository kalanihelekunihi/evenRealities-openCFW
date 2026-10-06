# Independent review P2-18509

Status: partial, unaccepted. No source or gate changes.

Fresh GNU replay confirms the 96-byte span `0x460910..0x460970`; instruction/reference manifests match. On mismatch, R1=1 and R0=low8(R4) are passed to `0x4604C2` with live R2/R3; its result is ignored and R0 is then set to `0xFFFFFFFF` before the external branch to `0x460D56`.

On match, the wrapper `0x46018E` is called with incoming R0-R3 live, then arguments are set for `0x43C0E4`: R1=1040, R2=0, and R0/R7 point to the literal at `0x46136C`, with live R3. R7 is then reset to index zero and the external test at `0x460B02` decides whether execution reaches the body. The body uses R9 as a source stride and R8=52 as destination stride. For each entry it reads source word at `R5 + R9*R7 +48`, writes key at `R6 +52*R7 +48`, then writes 4094 at +36, byte 1 at +40, and literal `0x461370` at entry offset 0, in that order.

R9's source-stride origin and the external test remain unresolved here; no bound is visible in the body. Fresh reads and possible source/destination aliasing are retained. Later continuation and child semantics are not inferred. Partial/unaccepted only.
