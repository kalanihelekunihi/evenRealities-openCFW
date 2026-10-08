# P2-21121 independent review

Status: partial / unaccepted. No source or gate changes.

Fresh replay passed for 0x480540..0x4805C0 (128-byte middle fragment); instruction/reference outputs match candidate. The V/S predicate uses separate short-circuit fresh observations. Its selected path reads a separate byte at offset 52, inverts bit 0, and stores a normalized byte; the false path writes zero. A later independent set of three fresh flag bytes is ORed and narrowed only for the branch. Nonzero executes five ordered independent word RMWs; each operation reloads the word after the previous store. The fragment ends with the inherited 16-byte frame active. No cached field or combined-RMW rewrite is justified.
