# P2-21119 independent review

Status: partial / unaccepted. No source or gate changes.

Fresh replay passed for 0x4804AA..0x480540 (150-byte middle fragment); instruction/reference outputs match candidate. The three predicates retain distinct short-circuit V/S reads and unsigned threshold behavior. Repeated V==33 checks are separate observations, and each byte output write occurs before the next predicate reads its fields. Thus aliasing can affect later results; no caching or collapsed state table is justified. The fragment leaves the inherited 16-byte frame active and performs no helper call or unwind.
