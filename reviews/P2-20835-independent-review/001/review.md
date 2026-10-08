# P2-20835 independent review

Status: **partial / unaccepted**.

Fresh replay passed for the pinned table at 0x6983A8..0x6987A8: 1024 bytes/256 little-endian words; image and source receipt hashes match, and the literal at 0x47CC14 resolves to the table start. Independently recomputed every entry as eight MSB-first shifts from index<<24 with conditional XOR 0x1EDC6F41, and all 256 match. The helper index is a byte XOR the state top byte, bounded to 0..255. This confirms the recurrence in the table, not an external protocol or complete ownership claim.
