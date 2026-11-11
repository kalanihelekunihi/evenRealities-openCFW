# R1 glasses connection-role policy in C

`r1/src/application/board/native_glasses_role.c` supplies the decision policy
and diagnostic sequence for application `0x4d654` (430 stock code bytes).
The final phone/glasses collision fault transition remains the explicit import
`r1_glasses_role_conflict_fault`; this is a partial behavior candidate, not a
complete architectural reconstruction of the function.

The input remains a full 32-bit word. Only exactly 65535 is rejected as the
invalid handle. A valid input matching a non-invalid phone handle enters the
collision assertion. An unassigned glasses field receives the input's low
16 bits, then reports status through the existing publisher. An already-set
field is retained. Native repeated volatile reads, logging modes, severity,
argument order and field reloads are preserved, including values wider than
16 bits that stock accepts before truncating its store.

The native tail adapter at `0x5e1dc` turns `(2,1,0)` into publisher arguments
`(1,1,0,2)` at `0x5e118`; the C policy calls the existing publisher with those
arguments. The actual shared phone/glasses field owners remain unchanged.

## Assertion boundary

On collision, stock logs the conflict, delays 500 ticks and prints the assertion,
file, line 1017, function and expression diagnostics. It then writes a word on
its stack and executes `BLX` to that stack address. The C unit reproduces the
diagnostic prefix and calls an unresolved architecture boundary. It contains
neither that opcode word nor a substitute trap or executable array.

Replay intercepts stock before the stack branch and models a returning boundary
on both paths. It does not execute the stack or validate exception delivery.
The native attempt has a 32-byte frame; the C boundary call is a zero-frame
tail. That difference is retained and is not treated as architectural equality.
Fault delivery/recovery requires further evidence and implementation.

## Validation

The production object passes 1,520 paired stock/C cases, including 162 modeled
collision cases. Cases cover invalid and wide input words, existing/unassigned
fields, all basic log modes, changing full-word modes, both PRIMASK states and
field mutations during providers. Bounded hooks compare field access order,
widths and values. Provider arguments, diagnostics, state, restored SP/callee
registers and interrupt masks match. Non-fault providers preserve the native
32-byte frame or verified zero-frame tails, including restored LR and callee
registers at terminal publication/log calls. Adjacent fields survive.

A further 160 cases execute actual C startup, its installed router, the new
role policy, context helper and SDK connection-index code together. These
normal non-conflict paths match stock state and calls. The router's existing
40-versus-32 frame gap and private-output normalization remain applicable;
this integration does not remove them.

Five negative controls reject narrowing the input, overwriting an existing
role, writing the phone field, skipping collision handling and publishing the
wrong event. Log/mode providers, delay, retained printf, status publication and
the fault transition are modeled. Internal nonargument registers, APSR, private
spills and timing are excluded. No real exception recovery, status-ring side
effects, scheduler or physical BLE behavior is established. REA's root and
fault-attempt windows match the locked application.

## Build and qualification

`build/sources-goal-r1-glasses-role-c/report.json` compiles all 598 units
(524 application, 74 bootloader). Both relocatable compositions pass without
failures or duplicate strong symbols. All prior 597 objects are unchanged.
Resolving role assignment exposes the fault-boundary import, so totals remain
158 application and 34 bootloader imports. `make sources-check` passes with
402 R1 source files.

Qualification compiled the unit but selected no regions. The canonical source
plan is unchanged. The fresh hybrid application retains SHA-256
`0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a`
and totals of 4,271 source-built, 641,889 binary-pull-through and 248 resource
bytes. Complete C firmware, instruction identity and physical role assignment
remain unproven.

The stale composition-summary JSON from the router step was regenerated after
correcting its historical comparison: that newly introduced router import did
not belong in the old baseline's removed-symbol set. Current summary readback
now agrees with this build; the underlying build reports were unaffected.

The [receipt](glasses-role-c-review.json) records source/object identity, REA,
both replays, negative controls, the unresolved fault transition and audits.
Probes are under ignored `build/goal-r1-glasses-role-c/`.
