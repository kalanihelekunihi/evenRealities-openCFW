# SEGGER RTT receive driver in C

Normal source composition now supplies `SEGGER_RTT_ReadNoLock` and
`SEGGER_RTT_Read` from `native_rtt_read.c`. They reuse the existing SDK
control-block allocation, native C initializer, and native up/down buffers.
The selected SDK write graph remains unchanged. Its full receive graph is
not pulled in, avoiding another private initializer/default-buffer pair.

REA confirms the locked entry at `0x3194c` and its real unlocked target at
`0x31964`, including the control-block literal. Stock reinitializes whenever
the first signature byte differs from `S`; the public template's zero-only
initialization check would miss other invalid signatures. The C driver uses
the native condition and the existing initializer.

The unlocked reader snapshots the write/read offsets, copies the tail segment
when wrapped, then the remaining segment, and publishes its new read offset
only after reading bytes. The write snapshot remains fixed across copy calls.
The locked wrapper uses ACLE register intrinsics to save BASEPRI, set 32,
and restore the prior low byte. No handwritten assembly is added.

7,792 warm stock/C pairs cover small-ring exhaustive cases and every pair
of read/write offsets in a 64-byte ring, both configured channels, capacity
boundaries, locked/unlocked entry points and interrupt masks. Host write
offset changes injected at copy entry verify snapshot behavior. Another
1,024 pairs execute cold reinitialization for four invalid signature bytes,
with optional host input immediately after initialization returns. Actual
native/C copy routines and the shared native initializer execute; no copy or
initialization result is substituted.

Checks compare returned lengths, received bytes, complete control-block state,
up/down buffers, destination guards, provider masks, SP, callee-saved registers
and final interrupt masks. Four compiled defects are rejected: zero-only
signature checking, mask 64 instead of 32, omitted wraparound, and rereading
the host write offset after a copy. The normal probe is rerun afterward.

All 804 R1 units compile without failures or duplicate strong symbols.
Imports remain 69 application and 22 bootloader linker symbols. All 801
nongenerated prior object hashes are unchanged. The two generated boot
objects retain source hashes, allocated bytes and relocation identities.
The composition contains one initializer, one control block and one native
buffer pair. Strict bootloader linking and R1 source checks pass; global
source checking retains the unrelated unlisted G2
`resident_rom_thumb_set.S` failure.

This verifies valid configured channels and ring geometry with nonoverlapping
destinations. It does not establish physical debugger timing, arbitrary
concurrent reconfiguration, atomic multiword snapshots or fault delivery.
The manager worker, console tokenizer/dispatch, startup placement and full
application linking remain unfinished. No source-plan selections change.
[The machine-readable review](rtt-read-c-review.json) binds source, SDK, REA,
build, ownership audit and execution evidence.
