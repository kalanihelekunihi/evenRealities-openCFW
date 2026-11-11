# Direct C stuck-charge recovery

The native-frame contract below is superseded by the [ordinary C recovery ABI](battery-recovery-pure-c-review.md). It remains historical evidence of the earlier implementation.

`board/native_battery_recovery.c` now supplies stock `0x3db70` directly in C.
The naked assembly bridge and separately framed kernel are removed. The native
saved R1/R2/R3 span is also the outgoing log-argument area: the C compiler's
natural argument stores now create that overlay, and the final three words
return through empty fixed-register constraints. This preserves timestamp
aliases into the span without a separate mirror buffer.

REA verified the 412-byte stock code, literals and string envelope. The C root
keeps the 40-byte provider frame and native live R4-R9 phases, while R10/R11
remain unchanged. Short-lived address observations avoid retaining an extra
device pointer across calls. The 64-bit elapsed-time threshold, sentinel/history
updates, voltage thresholds, cached reference, percentage clamp, timestamp
publication and separate logging-mode reads remain in C. This unit has no
executed inline assembly instructions.

The normal product object passes 4,288 paired stock/C cases (8,576 executions).
Tests cover timer wrap, zero/large frequencies, threshold boundaries, state and
voltage branches, estimates, changing log modes, all live R4-R11, full returned
R1/R2/R3, log arguments and visible storage, saved registers, SP and masks.
Eight callback mutation modes modify device/runtime fields and log stack words.
The timestamp is separate or aliases saved R1, R2 or R3. Guarded YHM storage
remains distinct from the battery runtime. Logging preserves untouched words,
including the third word when the SDK logger uses only two stack arguments.

Four compiled policy/ABI negatives are rejected: narrowing the frequency
threshold to 32 bits, losing saved R2, clearing the third log word and reloading
the reference after callbacks. Additional compiled layouts fail either live
register observations or the 40-byte frame. The previous bridge reaches its
first tick getter at 80 bytes. Strict GCC compiles but uses 56 bytes, so GCC
behavior remains unqualified.

All 579 R1 units compile and compose without failures or duplicate strong
symbols. The 578 unrelated objects, strong export set, manifest and imports
(164 application / 34 bootloader) are unchanged. Scoped qualification compiles
the unit but selects no exact region. This behavior/frame proof does not
establish full-root byte identity.

The canonical hybrid retains SHA-256
`0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a`,
with 4,043 selected source bytes, 642,117 binary fallback bytes and 248 resource
bytes. Counts include assembly and data elsewhere. The current normal report
is `build/sources-goal-r1-recovery-root-c/report.json`.

[Machine-readable evidence](battery-recovery-root-c-review.json) records hashes,
REA observations, audits and retained counterexamples. Probes live under ignored
`build/goal-r1-recovery-root-c/`. Tick, frequency, reset, curve and log providers
are modeled. Physical charging/timing, APSR, other caller-clobbered state,
arbitrary private-frame aliases, faults and concurrency remain unproven.
Original Arm Compiler 5 is unavailable. Complete source-only, byte-identical
firmware remains incomplete.
