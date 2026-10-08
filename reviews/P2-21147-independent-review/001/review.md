# P2-21147 independent review

Status: partial / unaccepted. No source or gate changes.

Fresh replay passed for 0x480B66..0x480BC2 (92 bytes); instruction and literal-reference outputs match. Unlike mode 3, the masked original word remains in R0 and contributes to the first configuration word. The subsequent fixed OR constants are applied before the first store. A separate second-word read is masked with literal ED4, ORed with 2, and stored. No helper calls occur in this fragment. The final POP places the scratch SP0 value in R1 rather than restoring entry R3. Other mode paths remain unresolved.
