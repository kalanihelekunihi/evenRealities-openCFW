# P2-21211 independent review

Status: partial / unaccepted. No source or gate changes.

Fresh replay passed for 0x481C48..0x481CF2 (170 bytes); instruction and literal-reference outputs match. Each z/t/j/q/b/default entry advances the argument cursor by four and stores it before testing the fetched target pointer. Null cases share the ADR 0x4826CC diagnostic path and do not write the target. Nonnull word variants store SP52 as a full word; j/q store the 32-bit counter as a sign-extended double word with the high word at target+4; b stores only the low byte. All mapped successful writes branch to 0x4824AC, whose output continuation remains outside this candidate.
