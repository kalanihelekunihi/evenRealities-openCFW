# Direct C TWI register-write adapters

`board/native_hw_twi_register.c` now supplies native register-write roots
`0x5505c` and `0x55120` directly in C. Both naked bridges and private kernels
are removed. Existing read function bytes and relocations remain unchanged.
The unit retains empty register/frame observations, with no executed inline
assembly instructions.

REA verified each stock code/literal envelope. The C roots keep the native
104-byte frame: outgoing argument at offset zero, 80 scratch bytes at offset
four and saved R4 at offset 84. Length 80 writes its final payload byte into
the saved R4 low byte; that effect remains observable on return. Length 79
preserves R4 and length 81 returns 9 before TX. The scratch is not enlarged
and length 80 is not rejected. Live R4 remains zero and supplies the outgoing
false `no_stop` argument; holding another zero adds a register and changes depth.

Raw TX status 17 returns immediately. Other nonzero statuses call the error
provider and retry with the current buffer/control state. A successful TX waits
500 ticks for primary or 200 for secondary, returning the wait result's low byte.
The existing C legacy-TX wrappers are reused rather than bypassed.

The normal product passes these paired stock/C suites:

| Suite | Cases | Observed depth |
| --- | ---: | --- |
| Direct adapter providers | 14,580 | 104-byte root frame |
| Actual C legacy-TX wrappers | 14,580 | SDK at 120 bytes |
| Actual bulk packet/register/wrapper C chain | 9,000 | SDK at 136 bytes |
| Null input, lengths zero and 81 | 24 | No invalid dereference |

Checks include byte-address inputs, register-byte truncation, full raw statuses,
retry order, control bytes, buffer bytes, callback mutations, controlled
input/frame/argument aliases, all live R4-R11, final saved registers, SP and
masks. The direct matrix includes 1,800 length-80 cases per suite. In the full
bulk chain, the child overlap remains while the parent restores the original
caller's R4 and returns native R2/R3. The unchanged short length-one path retains
its separate earlier proof.

Five compiled controls are rejected: rejecting length 80, enlarging scratch,
truncating TX status before comparing 17, changing the timeout and holding a
separate false value. The old bridge reaches SDK TX at 176 bytes instead of
native 120. Strict GCC remains blocked by existing SDK unused SVC parameters;
a diagnostic compile with only a probe-level warning override succeeds but
enters direct TX with 112 bytes instead of 104. Product warnings are unchanged.

All 579 R1 units compile and compose without failures or duplicate strong
symbols. The 578 unrelated objects, manifest, strong exports and composed
imports (164 application / 34 bootloader) are unchanged. The unit no longer
calls `nrfx_twim_tx` directly; the existing C legacy wrappers own that dependency.
Scoped qualification compiles both owners but selects no exact region.

The source plan and canonical hybrid retain SHA-256
`0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a`,
with 4,043 selected source bytes, 642,117 binary fallback bytes and 248 resource
bytes. Counts include assembly and data elsewhere. The current normal report
is `build/sources-goal-r1-twi-register-write-c/report.json`.

[Machine-readable evidence](twi-register-write-c-review.json) records REA results,
hashes, audits and counterexamples. Probes live under ignored
`build/goal-r1-twi-register-write-c/`. SDK TX, error and wait providers are modeled.
Wider address words, private return-address words, arbitrary control-frame
aliases, APSR, faults, concurrency and physical bus timing remain unproven.
Original Arm Compiler 5 is unavailable. Complete source-only, byte-identical
firmware remains incomplete.
