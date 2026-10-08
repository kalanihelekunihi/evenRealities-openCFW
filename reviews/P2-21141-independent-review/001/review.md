# P2-21141 independent review

Status: partial / unaccepted. No source or gate changes.

Fresh replay passed for 0x4809C4..0x480A32 (110 bytes); instruction and literal-reference outputs match. Dispatch uses UXTB and the enumerated 0–6 branches, with 7–255 routed to the default path. In mode 0, the source word is staged at SP0, low bits are cleared, and the optional byte1 test chooses OR 5 versus decimal 25 before the final store. Mode 1 clears low two bits and stores the scratch word. In both arms SP0 overwrites the saved entry R3 slot, so POP loads the resulting scratch value into R1. The remaining dispatch arms and full routine are unresolved.
