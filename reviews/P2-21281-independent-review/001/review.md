# P2-21281 independent review

Status: partial / unaccepted. No source or gate changes.

Fresh isolated replay passed for 0x482B00..0x482B56 (86 bytes); instructions and literal references match. The frameless initializer performs ordered zero writes before storing the rounded size `(size+3)&~3` modulo 32 bits. In the separate 16-byte routine, allocation and link-helper calls preserve live arguments and full returned pointers; each later head-word test is a fresh load. Head/tail links are written in the observed order, and the epilogue returns the allocation result in R0 with saved entry R3 in R1. Helper behavior and ownership remain unresolved.
