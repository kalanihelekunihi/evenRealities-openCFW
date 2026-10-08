# Independent review: P2-19151

Status: partial / unaccepted. No source or gate changes.

Fresh locked-byte replay for `0x469DDE..0x469E18` (58 bytes) matches the candidate instruction and reference records. The six SP12 word tests are separate fresh reads, in order: 8, 11, 5, 6, 224, 4094. The matching case calls `0x45A8EE` with `(34,0,0,100)`. The shared early return writes R0=0 only on the matched case, while the earlier rejection error can enter the same cleanup retaining its R0. `ADD SP,24` skips 20 local bytes and the saved incoming R3 slot, then POP restores the remaining frame. `0x469E18` is an in-function continuation with frame intact, not a newly inferred function entry.
