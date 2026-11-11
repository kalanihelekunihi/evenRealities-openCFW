# RTT C write dependency graph now participates in R1 composition

The pinned SDK `SEGGER_RTT.c` now supplies `SEGGER_RTT_WriteNoLock`, its private
write helpers and the 120-byte `_SEGGER_RTT` control block to the normal build.
The source is unmodified. Its SDK initializer remains outside the selected
graph, preserving the existing R1 initializer without a duplicate definition.
Application imports decrease from 204 to 202 by resolving the write routine
and control block, with no added imports.

REA confirms stock `0x31a18` selects its ring from the control block at
`0x2002e62c`, then implements skip, trim and blocking modes through availability
and copy helpers. Other flag values return zero. The stock body does not
initialize RTT on entry, matching the pinned routine's documented contract.
The existing R1 initializer still owns the native buffer sizes and pointers.

`sources.py` now supports explicit retained roots for a compiled unit. The
manifest selects `SEGGER_RTT_WriteNoLock` and `_SEGGER_RTT` with an ARM
relocatable section-GC link. This keeps their dependency graph and preserves
the complete original compiler object and symbol inventory in the report.
The selected object exports exactly those two strong symbols and imports only
`memcpy`; that import was already resolved in the normal application build.
Duplicate and unresolved-symbol checks use the selected object. This is not
an executable-byte transplant, stub or firmware-byte qualification.

The build tests exercise a retained function's code/data dependencies while
discarding an unrelated duplicate provider and its missing import. Failure
tests cover an undefined root, missing linker and a linker that reports success
without producing output. Failed selection never publishes the full object
or its definitions as a fallback. All 21 build-tool test methods pass.

`build/goal-r1-rtt-selected-write/verify.py` passes 14,652 paired cases
(29,304 executions) against stock. Cases cross both up-buffer indices,
ring sizes 2,3,8,16, valid read/write offsets, skip/trim/block/invalid flags,
and lengths around capacity and wrap boundaries. The probe checks independent
expected payload/offset results, return values, complete control-block and
buffer memory, control-block commit writes, source-data preservation,
callee-saved registers, stack restoration and interrupt masks. The stock ring
helpers execute; both graphs execute the same stock memcpy boundary, so this
comparison does not validate a C replacement for libc copy.

The final report `build/sources-goal-r1-rtt-selected-write-final/report.json`
compiles all 567 R1 units without failures or duplicate strong symbols.
Imports are 202 application and 34 bootloader. `make sources-check` passes.
[Machine evidence](rtt-selected-c-write-review.json) binds the REA snapshot,
selection commands, raw/selected objects, build-tool source, tests, execution
probe and normal report by hash.

Blocking tests require enough initial ring space; host-draining progress,
concurrent producers, malformed offsets/pointers, live debugger behavior and
physical hardware operation remain unproven. The C write body is 120 bytes
and not byte-qualified. The canonical source plan and G2 workflow gates are
unchanged; complete source-only linking remains unfinished.
