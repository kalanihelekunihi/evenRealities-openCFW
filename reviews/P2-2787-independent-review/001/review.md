# Independent review 2787

**Result: PASS_SCOPED.** Static decode verified all 129 instructions in `[0x429E00,0x429F68)`, with source/body/artifact hashes matching. The listing supports profile publication, the temporary high-seven-bit target and restore, control-field writes, the ordered gate clears, low-seven-bit restore, secondary call, and packed return/frame. No dynamic execution is claimed.

- Wait/service and dynamic branches are not tested.
- Changing reads, caller ownership, and physical hardware effects remain unresolved.
- Private evidence only; no canonical admission.
