# IRQ enable-state evidence

The pinned ISA manual's printed pages297 and299 define NIE as saving EPC/EPSR
then setting PSR.IE and PSR.EE, and NIR as restoring the complete PSR from EPSR
and returning to EPC. Printed pages180 and182 define IPOP/IPUSH stack transfers
without an enable-bit change. The authenticated NationalChip core_ck804.h puts
IE at bit6 and EE at bit8. Existing manual and SDK hashes are verified before
running the new enable-state check.

The decoded wrapper is traced with100 combinations of incoming handler PSR,
saved interrupted EPSR and returned callback PSR. The handler-entry values
are parameters, not a claimed hardware exception-entry rule. NIE sets both
bits, preserving the other incoming bits. From the next boundary through the
call, both remain set. At the return-side boundaries, enable state instead
reflects the supplied callback PSR. NIR restores the full supplied saved EPSR.
Thus callback-only nesting is insufficient coverage, and checking restore-side
stack boundaries is necessary even though callbacks may sometimes mask IRQs.

All100 cases and21 IRQ regression tests pass. Four new tests reject duplicate
NIE, an unreviewed PSR-writing instruction and a changed dispatcher, and check
a callback clearing IE/EE while NIR restores a saved PSR with IE set.

This is an instruction-semantic check, not proof of interrupt eligibility.
Priority-controller acceptance, arrival timing, stack-access faults, callback
PSR behavior and available stack remain separate. The prior234 all-boundary
stack checks form a conservative schedule including boundaries where IE may
be clear; they do not claim the hardware can interrupt at all those points.
IRQ source remains unadmitted and no firmware package is changed.
