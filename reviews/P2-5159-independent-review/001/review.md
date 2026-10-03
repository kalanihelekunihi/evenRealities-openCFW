# Independent review P2-5159

**Status:** PASS_SCOPED  
**Accepted:** false

Source-pinned isolated replay passes for the optional-field region. Fresh helper predicates gate individual append calls; offset updates remain wrapped and child returns are used as lengths without status checks. ADR literal targets and the outer option-mask gate match the instructions.

## Limits

Continuation at 0x7920 is excluded. Append-helper and option-query effects, buffer safety, and hardware behavior remain unresolved; private partial, accepted:false.
