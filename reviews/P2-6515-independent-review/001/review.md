# Independent review 6515

Disposition: **PASS_SCOPED**; `accepted:false`.

Both source hashes match. GNU Thumb decoding confirms two separate 16-byte wrappers using the same literal base at 430468. The first repeatedly reads the signed halfword at base+2; the second reads base+4. Each passes the fresh signed halfword and zero to 41DF48 with the current SP as its output pointer, then reloads R1 from `[SP]` before each subsequent helper call. The same halfword is reread before calls to 41DFC6 and 41E09A; each call result is ignored in the wrapper.

Both epilogues use `POP {R0,R1,R4,PC}`, so the two output stack words are returned through R0/R1 and R4 is restored. The output slots are not initialized by these wrappers before the first helper call, and the helper's write extent/failure behavior is outside this packet.

No canonical files or gates changed.
