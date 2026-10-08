# P2-21137 independent review

Status: partial / unaccepted. No source or gate changes.

Fresh replay passed for 0x480874..0x480920 (172 bytes); instruction and literal-reference outputs match the candidate. The five initial output words are loaded/stored in order. Subsequent source and table observations are independently reloaded, including the three six-byte-stride halfword selections; these are not a shared snapshot. The output48 value is masked and stored, then reloaded and ORed with the low nibble from a fresh word before the second helper call. Both helper results are ignored. The prefix has no epilogue, so later control flow and frame restoration remain unresolved.
