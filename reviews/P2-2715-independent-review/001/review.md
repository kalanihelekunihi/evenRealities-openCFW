# Independent review 2715

**Result: PASS_SCOPED.** The static verifier decodes the full 312-byte body interval `0x428506–0x42863E` as 109 original Thumb instructions. Source, body, and candidate artifacts match their hashes. The pseudocode follows the decoded field extraction and ordered publication stores, conditional wait branch, fresh control-register read-modify-writes, secondary helper call, packed return, and 32-byte frame restoration. This packet makes no dynamic execution claim.

- Child semantics, input bounds, changing reads, caller ownership, and hardware effects remain unresolved.
- Private evidence only; no canonical admission.
