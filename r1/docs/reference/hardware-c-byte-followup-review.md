# Hardware C byte-qualification follow-up

The canonical source plan now includes the C touch-ready IRQ callback at native
`0x933fc`, exactly six bytes. Its compiled body sets event flags to one and tail
calls `r1_touch_task_event_post` at `0x93504` (Thumb target `0x93505`). The official
qualifier independently anchors the entry, recovers the branch relocation and
checks all linked bytes against the locked application. No opcode array or
replacement reference is used.

The run scoped only `qualify_sources.candidates()` inputs to eight existing
hardware source units: touch board, peripheral bindings, YHM transport, LIS
auxiliary/setup, BMA reads/interface and QMA configuration. The official compile,
match, relocation and linked-equality logic remained unchanged. All 40 recorded,
O2, Os, Oz and Og compilations succeeded. Five regions qualified; four YHM regions
were already covered, leaving this one new six-byte region. All other bodies
remain unqualified; nonselection is not a behavior failure or proof that no
future compiler/source improvement can qualify them.

The merged candidate plan was tested before promotion. Its complete hybrid
application equals the locked stock byte for byte, SHA-256
`0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a`.
Source-built coverage increases from 3,827 to 3,833 bytes; unclassified binary
pull-through decreases from 642,333 to 642,327 bytes; resources remain 248 bytes.
The canonical plan is exactly the tested merged plan. Source completeness remains
false. The callback's target is still a native-address binding in this hybrid.

The source is unchanged from the 12,800 paired touch-board comparisons in
`touch-ready-c-snapshot-review.json`, which execute the actual native/C IRQ and
event-forwarder with modeled OS flags. This follow-up adds byte identity, without
expanding physical IRQ or RTOS/electrical proof. The current normal R1 build remains
573 compiled units and 197/34 application/bootloader imports; `make sources-check`
and `git diff --check` pass. No G2 gate advances. Exact qualifier, source, plan,
behavior-evidence and hybrid-report hashes are bound in the companion JSON.
