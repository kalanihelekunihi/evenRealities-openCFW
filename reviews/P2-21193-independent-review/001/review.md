# P2-21193 independent review

Status: partial / unaccepted. No source or gate changes.

Fresh replay passed for 0x481836..0x481884 (78 bytes); instruction and literal-reference outputs match. The push and allocation establish a 232-byte frame. The prefix preserves callback state at SP16, callback address at SP192, fifth argument at SP232, and its low byte at SP67. Each loop first peeks a byte without advancing; the later callback byte is a separate post-incrementing LDRB. The callback receives the recorded live state/address/register arguments and its full result replaces SP16; zero branches to the unresolved failure path, while nonzero increments the SP52 counter and retries. NUL terminates to an unresolved exit; percent initializes six words in order before branching to the parser. Final return and unwind are outside this prefix.
