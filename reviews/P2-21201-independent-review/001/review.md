# P2-21201 independent review

Status: partial / unaccepted. No source or gate changes.

Fresh replay passed for 0x4819BE..0x481A28 (106 bytes); instruction and literal-reference outputs match. The chained subtraction and unsigned branch sequence yields the candidate’s exact byte-to-target mapping for percent, the listed letter conversions, and the default case. I treated R11 as the retained original conversion byte and R1 as the residual value at each branch, without substituting conventional format-specifier behavior for the branch structure. The percent path writes 1 at SP28, sets R1 to 37, and branches to 0x48248E. Handler bodies, common emission, and routine return remain unresolved.
