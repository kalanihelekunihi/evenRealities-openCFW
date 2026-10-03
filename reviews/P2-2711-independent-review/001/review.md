# Independent review 2711

**Result: PASS_SCOPED.** Static Capstone extraction passed and verified exact coverage of the 292-byte interval `0x4283E2–0x428506` with 101 decoded Thumb instructions. The body hash and candidate file hashes match the receipt. The original decode supports the described register saves, stack packed return construction, profile pointer calculations, field loads and stores, conditional wait branch, temporary low-seven-bit RMW, delay call, restore, and epilogue. This packet is static mapping evidence only; its verifier does not execute the handler.

- No dynamic execution is claimed here.
- Child semantics, bounds, changing input reads, caller ownership, and hardware effects are not established.
- Private evidence only; no canonical admission.
