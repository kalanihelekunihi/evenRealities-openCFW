# P2-21265 independent review

Status: partial / unaccepted. No source or gate changes.

Fresh isolated replay passed for 0x4827B0..0x482868 (184 bytes); instruction and literal-reference outputs match. The descriptor predicate and error path, including the diagnostic write to saved SP0, match the candidate account. The normal path repeatedly reloads count during scan, allocation, descriptor update and copy; helper arguments and zero-result allocation exit are preserved. On match, the new base is stored before descriptor count is updated. The copy loop's unsigned `count >= index` condition is inclusive, and duplicate key matches skip copying without a separate count decrement. The final helper and POP path return the recorded old base/boolean while SP0 may alter the saved R3 return slot. Helper contracts remain unresolved.
