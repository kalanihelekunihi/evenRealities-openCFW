# Independent review 2755

**Result: PASS_SCOPED.** Static decoding verified all 77 original instructions over `[0x42944A,0x42951C)`, with source/body/artifact hashes matching. The listing supports profile publication, low-seven-bit restore, conditional wait/service path, packed return and frame. The following literal pool is excluded.

- Wait/service and dynamic behavior are not tested.
- Caller ownership, changing reads, and physical hardware behavior are unverified.
- Private evidence only; no canonical admission.
