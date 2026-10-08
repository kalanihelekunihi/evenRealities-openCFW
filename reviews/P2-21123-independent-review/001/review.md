# P2-21123 independent review

Status: partial / unaccepted. No source or gate changes.

Fresh replay passed for 0x4805C0..0x4806A6 (230 bytes); instruction/reference outputs match candidate. Priority flag paths and version predicates follow the recorded short-circuit ordering, retaining distinct fresh V/S observations and unsigned thresholds. Literal values are stored as loaded; branches map them to their enumerated table offsets, including late offset-24/28 overrides. The alternate flag paths have their own literal sequences and can skip lower-priority predicates. No prior table clearing or initialization assumption is made. The fragment continues at 6A6 with the 16-byte frame active.
