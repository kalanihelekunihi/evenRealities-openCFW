# Independent review 2771

**Result: PASS_SCOPED.** The static verifier decodes all 169 instructions in `[0x42984E,0x429A1E)` exactly, excluding the adjacent NOP. Source, body, and artifact hashes match. The original listing supports the three saved stack values, indexed chunks, fixed-base low-field arithmetic, high/low temporary writes and staged restores, delays, and return registers. This map is static evidence only.

- Dynamic arithmetic and wait/service execution are not established.
- Caller ownership, changing inputs, and physical hardware effects remain unresolved.
- Private evidence only; no canonical admission.
