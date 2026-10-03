# Independent review 2871

Status: **PASS_SCOPED** (`accepted: false`).

The source hash matches the inventory image; the body `[0x4213D8, 0x421548)` matches its claimed digest. The candidate receipt and listed artifact hashes match. Its isolated Unicorn replay passed all 8,640 fixtures, with the output redirected to a fresh review-specific directory.

I checked the decision model against the original Thumb instructions and the decoded literals. The selector limit branches, null-destination and invalid-selector handling, unsigned wrapped `offset + count` comparison, enabled-bit gates, source selection, the selector-1 adjustment path, provider arguments, and final status values agree with the body. In particular the address helper adds `0x280` only at unsigned offsets at least `0x200`; address arithmetic then wraps as described. The call target is controlled to return `0xDEADBEEF`, while the caller returns its own success status, consistent with the original caller instructions.

The replay establishes decision and call-argument behavior for its enumerated matrix only. It does not perform a copy or establish provider storage or hardware behavior. No whole-image completeness or canonical admission is claimed.
