# Independent review 2739

**Result: PASS_SCOPED.** The static verifier decodes exactly 74 original Thumb instructions across `0x428D90–0x428E6A` (218 bytes). Source, body, and candidate artifacts match their hashes. The listing supports the handler’s frame and packed return, profile-field loads and six publication stores, bounded wait followed by service invocation, secondary helper call, and epilogue. This independently confirms the handler10 address range; it is a static map, not execution evidence.

- Wait/service and dynamic paths are not exercised.
- Bounds, caller ownership, changing reads, and physical hardware behavior remain unresolved.
- Private evidence only; no canonical admission.
