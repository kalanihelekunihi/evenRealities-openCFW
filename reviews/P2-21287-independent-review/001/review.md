# P2-21287 independent review

Status: partial / unaccepted. No source or gate changes.

Fresh isolated replay passed for 0x482C0E..0x482C9A (140 bytes); instruction/reference outputs match. A null descriptor returns zero through the 16-byte POP path. The two endpoint-equality paths preserve their field store, fresh reload, and helper-call ordering. The interior path makes four ordered helper calls and overwrites the incoming node register with a later helper result; its return is therefore path-dependent. No node-membership, null-node, or release semantics are inferred.
