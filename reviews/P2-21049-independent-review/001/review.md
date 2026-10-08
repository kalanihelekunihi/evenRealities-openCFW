# P2-21049 independent review

Status: partial / unaccepted. No source or gate changes.

Fresh replay passed for 0x47F56E..0x47F5F6 (136 bytes); instruction/reference outputs match candidate. The 8-byte helper entry preserves three distinct full-result branches: zero returns zero, first nonzero invokes and returns a second helper result, and second zero triggers an ordered word OR/store and third helper whose full result returns without normalization. The next entry establishes a 40-byte frame, calls the helper with LOW8 entry index, and exits on full result or an indexed mask hit. A fresh indexed-word bit test only sets the flag for LOW8 index 23 when bit 27 is clear; otherwise control continues with the frame active. This is a prefix, so no unwind/return claim. External helper and pointer semantics unresolved.
