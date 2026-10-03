# Independent review 6587/001

Disposition: **PASS_SCOPED**; `accepted:false`. Packet, input, and body hashes match. GNU Thumb decoding confirms the six local entries in 0x416026..0x4160E8: a permanent self-branch at 0x416026; a `BX LR` no-op; context predicate reading IPSR then querying 0x418B56, and only when that result is not 1 consulting PRIMASK/BASEPRI; two status wrappers that preserve incoming R7 through POP into R1; and the final state wrapper that calls the predicate, checks a fresh context result and global word, writes global state 2, calls 0x418148 with result ignored, and returns zero on its success path.

The conditional short path when 0x418B56 returns 1 bypasses mask reads. The global state reads/writes are separate operations, not atomic. The wrappers' exact status branches and aliases agree with the packet. This does not establish the purpose of the queried global or child semantics. No canonical files or gates changed.
