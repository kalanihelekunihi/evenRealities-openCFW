# P2-21189 independent review

Status: partial / unaccepted. No source or gate changes.

Fresh replay passed for 0x4816C6..0x48173A (116 bytes); instruction and literal-reference outputs match. The unsigned sparse-index guards accept banks 0..6 and 7..13 corresponding to the recorded index ranges. For each set bit, the code finds the lowest set-bit slot, clears it from the working mask before reading the callback and argument words, then performs BLX with the mapped live arguments. The callback return is ignored. A null callback sets status 7 but processing continues; the argument word is still read. Thus callback arrays are freshly observed per bit and later entries may reflect callback writes. A zero mask returns without array reads. The 16-byte frame is restored; trailing padding is excluded.
