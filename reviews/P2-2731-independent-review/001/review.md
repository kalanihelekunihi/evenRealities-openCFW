# Independent review 2731

**Result: PASS_SCOPED.** Static decoding verified 74 original Thumb instructions exactly over `0x428BB0–0x428C84` (212 bytes). Source/body/artifact hashes match. Listing confirms frame and packed return construction, profile loads and six publication stores, optional bounded wait followed by service call, secondary call, and epilogue. The adjacent literal pool beginning at `0x428C84` is excluded. This is static evidence only.

- Wait/service and dynamic paths are not executed here.
- Input bounds, changing reads, caller ownership, and hardware effects remain unresolved.
- Private evidence only; no canonical admission.
