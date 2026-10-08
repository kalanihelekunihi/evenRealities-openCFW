# P2-21047 independent review

Status: partial / unaccepted. No source or gate changes.

Fresh replay passed for 0x47F46A..0x47F56E (260 bytes); instruction and reference outputs match candidate. The initial equality comparison bypasses the update block. On the unequal route, a second fresh word/byte pair drives a signed compare within nonnegative byte ranges; the callback receives the fifth stack argument and its result is ignored. Low-three-bit field construction and RMW operations use independent fresh reads, including three separate mask clears at the end. The common POP’s SP0 overwrite changes the restored R1 alias only on the update path. No helper/global ownership or hardware contract inferred.
