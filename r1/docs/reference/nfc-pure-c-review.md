# NFC identity path without register-binding assembly

The ST25 identity adapter and board chip-ID probe in
`r1/src/application/st25/native_identity.c` now use ordinary C. The adapter
initializes word-sized scratch backing, registers the existing provider, calls
ReadID, reloads the ID byte for each enabled log and returns it. The board probe
retains acquire, 50 ms delay, identity read, release, outer logging and full-byte
return ordering. Provider status words do not replace the resulting ID.

The pinned ST25 driver supplies the footprint evidence: ReadID calls GetICREF,
which calls ReadReg with length one. The actual wrapper maps register 0x17 to
system-memory bus address 0xAE. The assembly previously captured/restored incoming
R3's upper scratch bits and bound the outer ID to R4. These are replaced by the
C byte-output and return-value contract. Upper scratch bytes, caller-clobbered
R3, exact private frame layouts and provider-visible inherited registers are
not retained as outputs. No caller is promised those values by the typed API;
the board probe consumes the returned ID value.

This intentionally does not claim the stronger incidental register/frame
contract of the earlier identity review. Word-sized backing is retained, so the
controlled full-word writes used by the probe still fit the allocated object.
The actual driver owns a one-byte view. Arbitrary aliases into surrounding stack
storage are outside this contract.

## Evidence and checks

REA readbacks `ev_6bfa81076f154c01a4401fc0e66a624c6164c177966b844a28cc5a322cc19dcc`
and `ev_0a4e0796cde9229cc3ff05ec4f7b116ed76d835c2dc4d353386923c2f353ebd5`
are checked against the preserved stock application bytes. The current Ghidra
session does not recognize the inner address as a procedure; these are byte
readbacks, not a newly obtained decompilation or caller-completeness proof.

`build/goal-r1-nfc-pure-c/verify.py` passes 15872 paired stock/C cases, covering
all 256 ID bytes, registration/read errors, no/byte/word read effects, changing
log modes and retained output-buffer mutations during modeled mode/log calls.
It compares the ID byte, ordered provider and logging calls, log strings/tags,
R0 return, final callee-saved registers, SP and interrupt masks. Private buffer
addresses are normalized. Registration receives no scratch pointer; arbitrary
registration-time stack peeks/mutations from the older probe are excluded.

`integration.py` passes 480 paired cases against the previous compiled adapter
while executing the actual pinned ST25 registration, ReadID/GetICREF/ReadReg and
board-binding sources. It covers recognized/unrecognized IDs, initialized and
uninitialized devices, all logging modes and I2C error/no-write cases. It asserts
0xAE/0x17/one-byte transfer arguments and compares resource/delay/log traces,
returned IDs, initialization and active-driver state. I2C transfer, resource,
delay, logging and EABI clear are modeled lower boundaries; electrical bus
behavior and timing are not exercised.

Four compiled defects—wrong delay, Boolean ID return, cached logging mode and
missing resource release—are detected, followed by a clean baseline rerun.
The source contains no inline assembly or explicit register bindings.

## Composition and remaining boundaries

The current report `build/sources-goal-r1-nfc-pure-c/report.json` compiles all
778 units, with no failures or duplicate strong symbols and unchanged
124 application / 22 bootloader linker imports. The identity object changes.
Two generated boot objects differ in debug-path metadata but retain identical
source hashes, allocated bytes and allocated-section relocations. The other
775 payload object hashes are identical. A strict bootloader link still succeeds
without undefined symbols. No source-plan/qualification selection is changed.

R1 source validation passes. Global sources-check retains the pre-existing G2
unlisted assembly-file failure. No NFC device or firmware was written. Physical
I2C, real delay, asynchronous callbacks, full application linking and hardware
boot remain outstanding.
