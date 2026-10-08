# P2-21175 independent review

Status: partial / unaccepted. No source or gate changes.

Fresh replay passed for 0x481364..0x4813BC (88 bytes); instruction and literal-reference outputs match. The fragment performs seven ordered loads from target pointers A0..B8. For each item, it reads the target word first, reloads the corresponding SP mask, ANDs, then stores the output word. The first mask uses the recorded R1 value; subsequent masks come from the SP4-based sequence. This order preserves possible aliasing effects and does not assume a coherent snapshot. The branch at 0x48145C and routine return remain unresolved.
