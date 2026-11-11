# R1 PMIC state-command record and registration

The existing `device_stacmd` provider now participates in relocatable
composition. Its C source and compiled object are unchanged. Current
execution of the hash-locked stock scatter loader, stopped before runtime,
recovers the 108-byte record at `0x200075C4`: configuration word 5, pin 33,
pull encoding 3, GPIO/delay callbacks, embedded device and nine-word operation
table. All 108 source bytes match after test-only name/callback relocations.
Relocating the local delay section checks its stored pointer, not delay-body
or timing identity.

REA observes the complete 18-byte registration body at `0x565F4..0x56605`,
inclusive. It copies the name into the embedded device at +48, installs the
operations pointer at +52, and tail-calls the registry with the device
address. The shared operations table begins at record +72. The source
returns the registry status; assembly/execution establish that propagation
despite the decompiler's inferred void signature.

All 54 stock-versus-source registration comparisons pass, covering three
registry results, three name words including null, three opened words and
optional mutation during the registry call. Checks compare the complete
record visible at the call, complete final record, device argument, call
count, SP and return status. The registry is mocked; this does not validate
its internal behavior or execute state-command operations.

All 562 R1 units compile and both compositions pass. The state-command record
import resolves, reducing application imports from 241 to 240; bootloader
imports remain 34. No new imports or duplicate strong symbols were added.
No source-plan entry, canonical pseudocode ledger or workflow gate changed.

No GPIO, delay or PMIC transaction was performed on hardware. Wire timing,
electrical effects, operation callback behavior, exact source qualification
and final firmware linking remain separate work. The source provider's delay
dependency is compiled but is not physically calibrated by this review.

[stacmd-registration-review.json](stacmd-registration-review.json) binds
scatter bytes, unchanged source/object hashes, report identity, REA evidence
and comparison counts. Probes and the neutral REA snapshot remain under
ignored `build/goal-r1-stacmd/`.
