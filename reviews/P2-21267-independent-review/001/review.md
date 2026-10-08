# P2-21267 independent review

Status: partial / unaccepted. No source or gate changes.

Fresh isolated replay passed for 0x482868..0x482900 (152 bytes); instructions and literal references match. The error branches overwrite saved stack slots before the diagnostic calls; the zero-key path then enters the explicit FFFFFFFF store loop, whose memory fault behavior is not inferred. The ordinary path reloads descriptor base/count for the reverse index scan, compares fresh key bytes, and writes the full replacement value at the matching reverse index. Resize helper arguments use the incremented count and five-times size; on nonzero allocation result the new base is stored before count/key-base reloads. The follow-on at 0x482900 remains unresolved.
