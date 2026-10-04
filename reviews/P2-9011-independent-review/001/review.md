# P2-9011 independent scoped review

Status: PASS_SCOPED; accepted: false; status: partial.

- The initializer map’s 51 Thumb instructions match the pinned image byte-for-byte; its literal references also match. The loop stores nine 44-byte descriptors in 3-by-3 traversal, preserving bytes it does not explicitly write.
- The final word store publishes 0x785250 at global 0x200610AC+60. The 16 bytes there decode as four odd Thumb table entries (0x53119D, 0x531331, 0x5315B5, 0x53135B); the callback slot at +88 is distinct.
- At 0x785250, the bytes begin ASCII “AttcIndConfirm”; this supports the flash-table interpretation without assigning table-entry semantics.

Limitations:

- No concurrency, full firmware behavior, or callback contract is established; this remains private partial evidence.
