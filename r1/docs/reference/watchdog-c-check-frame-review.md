# Watchdog check timestamp frame

`board/native_watchdog_manager.c` now supplies its C checker with the stock
saved R3 timestamp word at entry SP minus 16. A 10-byte bridge preserves the
native frame and restores that word to R3 on normal return. The timestamp
provider writes into explicit initialized machine state rather than an
uninitialized C automatic variable. The checker reloads that volatile word
when evaluating records.

Raw instructions at `0x5da4c` establish the saved-word sample destination,
unsigned wrapping timeout comparison, armed-record exclusion and fault sequence.
The remaining BASEPRI assembly is an actual CPU interrupt-priority operation;
it is not replaced with guessed C behavior. List/lock/sample implementations
remain the existing dependency boundaries.

All 6,912 stock/C comparisons pass across enabled states, zero-to-three nodes,
flags, timestamps and intervals, wrapping samples, zero/one/two/four-byte
provider writes and incoming R3 values. Checks compare normal-return R3,
provider trace and sample pointer, full controlled node state, fault-record
storage, invalid-write address/size/value, interrupt masks, normal-return
R4-R11/SP and provider-call alignment.

Two old-source counterexamples are retained. A normal sample returns raw R3
100 in stock but a clobber word in old C. With a provider that writes nothing,
stock's incoming zero timestamp does not expire the record, whereas old C's
uninitialized local causes the deliberate fault attempt. This is a controlled
provider-boundary discrepancy, not evidence of that failure occurring on a
physical device with the normal timestamp provider.

Expiry runs match through flag update, BASEPRI = 64, fault-record publication
and attempted four-byte zero write at `0xffffffff`. The emulator stops at the
write; exception handling and physical reset are unverified. Lock/list/sample
providers are modeled. All 562 R1 units compile without failures or duplicate
strong symbols; imports remain 211 application / 34 bootloader, other 561 units
are unchanged and source checks pass. Source-plan selections and G2 gates are
unchanged. Byte qualification and complete source-only firmware remain open.
Exact bindings are in the [machine-readable review](watchdog-c-check-frame-review.json).

The subsequent [direct C checker review](watchdog-check-c-review.md) supersedes this bridge implementation and strengthens provider-depth checks. The earlier fixtures and counterexamples above remain historical evidence.
