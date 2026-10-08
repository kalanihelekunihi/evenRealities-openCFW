# P2-21057 independent review

Status: partial / unaccepted. No source or gate changes.

Fresh replay passed for 0x47F85E..0x47F90C (174 bytes); instruction/reference outputs match candidate. R4 remains the saved status across callbacks, which receive fifth argument zero and separate SP16 reads; helper results are ignored. Index 20 writes its byte fields before the final common status helper; index 23 has its own early route. General routes preserve the wrapped `(SP8 << 2)` test, then independently test LOW8 index and SP8 mask. F902 routes call the status helper and return full R4; F908 early exits bypass that call. Shared teardown releases the inherited 40-byte frame. No status normalization or final readback inferred.
