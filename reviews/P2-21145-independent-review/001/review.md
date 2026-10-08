# P2-21145 independent review

Status: partial / unaccepted. No source or gate changes.

Fresh replay passed for 0x480AD4..0x480B66 (146 bytes); instruction and literal-reference outputs match. The initial masked word is staged, but R2 is replaced by the separately loaded byte before configuration construction, so the masked snapshot does not contribute to the final value. The later source/configuration stores follow the recorded order. The optional byte test chooses between a mask-and-OR update using literal ED0 and the clear-0x28/OR-8 path; both write the final SP0 value without a late source reload. The common POP returns current SP0 through R1, not the original saved R3. Other dispatch modes remain unresolved.
