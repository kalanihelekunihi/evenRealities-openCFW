# P2-21017 independent review

Status: partial / unaccepted. No source or gate changes.

Fresh replay passed for 0x47ED10..0x47ED76 (102 bytes); instruction/reference outputs match candidate. The first entry enforces the full object nonnull and mask high-byte-zero guards, then takes two independent full-word reads: first is the returned snapshot; second is masked and written. The 8-byte wrapper builds a message via the PC-relative address target and returns the helper result with shifted POP aliasing. The final leaf preserves the observed fallthrough word read and second helper call if the first helper returns. No callback/helper contract beyond the mapped behavior is assumed.
