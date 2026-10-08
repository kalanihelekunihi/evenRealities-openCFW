# Independent review: P2-19161

Status: partial / unaccepted. No source or gate changes.

Fresh replay of `0x469F16..0x469FA2` (140 bytes) matches candidate instruction and reference records. Ordered FULL selector comparisons are 10, then 72, then 73. Each recognized route creates its separate six-byte record at SP16, SP8, or SP0 and calls `0x464BB2(34, record, 6, 0)`. The shared epilogue adds 52 to SP and pops PC, skipping the saved R7 slot; R0 remains path-dependent (guard zero, child result, or original selector on the unmatched path). The next PUSH at `0x469FA2` is outside scope.
