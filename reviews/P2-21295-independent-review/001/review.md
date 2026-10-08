# P2-21295 independent review

Status: partial / unaccepted. No source or gate changes.

Fresh isolated replay passed for 0x482D88..0x482DD8 (80 bytes); instruction/reference outputs match. The frameless predicate short-circuits after a nonzero first endpoint and only reads the second endpoint when the first is zero. The wrapper returns saved R7 via POP. Each computed-link writer pushes before the node guard; null nodes skip descriptor/stack reads, while nonnull paths freshly load descriptor base and saved stack value, then store at the computed offset (with the second helper adding four). Return registers and alias-sensitive order match the candidate. No fixed field offset is inferred.
