# P2-21241 independent review

Status: partial / unaccepted. No source or gate changes.

Fresh isolated replay passed for 0x482348..0x4823DE (150 bytes); candidate instructions and reference outputs match. The modifier dispatch distinguishes byte, halfword, aligned doubleword, and ordinary word reads. Cursor updates are stored before narrow conversions; the doubleword path aligns `(cursor+7)&~7`, stores the cursor before the pair load, then advances by eight and stores again. The pair is saved at SP8/SP12. The subsequent flag-bit test and pair-zero check retain their branch order, and the hexadecimal-prefix path requires the full conversion test before writing its two bytes and advancing the count. The 0x48246C continuation remains unresolved.
