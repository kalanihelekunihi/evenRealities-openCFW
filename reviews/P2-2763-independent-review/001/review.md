# Independent review 2763

**Result: PASS_SCOPED.** Static verifier decoded 75 original instructions exactly over `[0x42962C,0x429700)` (212 bytes). Source, body, and candidate file hashes match. The instruction listing supports stack/packed return handling, profile field publication, indexed packed-byte selection to the low-seven-bit field at `0x40020048`, and the expected epilogue. The adjacent literal pool starts at `0x429700` and is excluded.

- Wait/service and dynamic paths are not tested here.
- Caller ownership, changing reads, and physical register effects remain unresolved.
- Private evidence only; no canonical admission.
