# P2-20969 independent review

Status: partial / unaccepted. No source or gate changes.

Fresh replay passed in an isolated output against the locked flash SHA-256 recorded in the candidate receipt. Fresh instruction JSON and reference records match the candidate exactly; the fresh disassembly differs only in assembler temporary-path text. Range is 0x47E3E6..0x47E470 (138 bytes).

Semantic audit confirms the full-word state comparison to 1 guards the first flag queries/calls and clear. The first and later diagnostic branches make fresh flag reads; helper and mask results are not the epilogue result. On the nonzero helper arm, the error logger can overwrite SP0/SP4 saved slots (97 and the corresponding literal), changing the shifted POP return; the zero arm clears the state word and bypasses that error block. The return is therefore stack-slot/path dependent. No unsupported external helper contract is inferred.
