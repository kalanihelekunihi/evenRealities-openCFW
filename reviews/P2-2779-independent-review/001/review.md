# Independent review 2779

**Result: PASS_SCOPED.** Static replay decoded exactly 86 original Thumb instructions in `[0x429B4C,0x429C46)`. Source, body, and artifact hashes match. The listing supports the six profile publication stores, fresh control-field writes, conditional wait/service path, delay-5 call, packed return, and frame restore. This is not a dynamic execution claim.

- Wait/service and dynamic input paths are not covered.
- Caller ownership, changing reads, and physical hardware effects remain unresolved.
- Private evidence only; no canonical admission.
