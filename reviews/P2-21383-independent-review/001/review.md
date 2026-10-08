# Independent review — P2-21383

Status: partial; accepted: false.

Fresh extraction passed for the two disjoint data spans, totaling 24 bytes. The regenerated raw-byte records match the candidate. I independently checked each little-endian word and confirmed the cited consumer-reference records: 0x483FCC in map 21728, 0x483FFC in 21730, 0x484000 in 21732, 0x484004 and 0x484008 in 21744, and 0x48400C in 21756.

This verifies the literal bytes and cited consumers only. Pointer targets, pointed-to data ownership, and the intervening 0x483FD0..0x483FFC region are outside the evidence here; no exhaustive ownership or code classification is claimed.
