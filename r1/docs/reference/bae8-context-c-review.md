# R1 BAE8 link-context lookup in C

`r1/src/application/board/native_bae8_context.c` supplies the missing
`r1_native_bae8_context_get` provider used by the BAE8 notification sender.
It replaces the manifest's unused SDK `ble_link_ctx_manager.c` unit, keeping
one implementation of stock application function `0x514e0` (72 bytes).
No source callers imported the removed `blcm_link_ctx_get` symbol.

The stock helper clears a non-null output first, checks the descriptor and
pool, checks the low two size bits through a byte read, obtains a connection
index, then reloads capacity, size and pool. Those reloads matter when the
connection-state query changes the descriptor. Capacity failure returns 4,
an absent connection returns 5, misalignment returns 7, and null inputs return
14. Successful pointer arithmetic wraps at the target's 32-bit word width.

The sender passes a full 32-bit connection value. Stock index/validity code
at `0x51e04`/`0x51fa4` rejects values of 20 or greater before querying flags.
The SDK's public lookup prototype accepts only 16 bits. A probe calling through
that prototype produced 72 differences in 1,280 cases: for example, `0x10000`
could become active connection zero. The C replacement guards the full word
before calling the existing SDK index API. This avoids narrowing an invalid
handle into a valid one. It does not change the architectural HVX SVC wrapper.

The current production object and compiled SDK index/validity functions were
compared with the stock helper and its actual index/validity chain in 11,520
paired Unicorn executions. Cases cover null inputs, capacity and size bounds,
wide handles, active/inactive flags, output aliases into the descriptor, and
descriptor mutations at the modeled flag query. Bounded memory hooks compare
descriptor read/write order, width and values. Return status, output, descriptor
state, flag calls, restored stack and callee registers match. Both paths reach
the flag query at caller SP minus 24 bytes. Internal saved-register values,
caller-clobbered registers, condition flags, private spills and instruction
timing are outside this contract. Four negative controls reject handle
narrowing, omitted output clearing, cached pool and cached size.

`build/sources-goal-r1-bae8-context-c/report.json` compiles/composes all 591 units
with no failures or duplicate strong symbols. The other 590 objects are
unchanged. Application imports fall from 157 to 156; bootloader imports remain
34. Qualification compiled the new unit but admitted no exact regions.
The canonical source plan is unchanged. The fresh hybrid application retains
SHA-256 `0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a`
and totals of 4,269 source-built, 641,891 binary-pull-through and 248 resource
bytes. These totals do not establish a complete C firmware build.

REA's 72-byte read agrees with the locked stock application. The durable
[receipt](bae8-context-c-review.json) records provenance and results. Reproducible
probes live under ignored `build/goal-r1-bae8-context-boundary/`. Flag queries
were modeled as canonical booleans; interrupts, MMIO, physical BLE behavior
and the entire send/observer chain were not validated by this lookup replay.
The service owner was unresolved at this lookup-only stage; the subsequent
[shared-state review](bae8-state-c-review.md) supplies it. The subsequent
[observer review](bae8-observer-c-review.md) supplies dispatch and credit
handling, with connection/write handler bodies still unresolved.
