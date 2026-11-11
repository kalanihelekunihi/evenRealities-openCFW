# Touch ready-byte and complete identity probe in C

`board/native_touch_transport.c` now supplies native `0x933dc` as
`r1_touch_ready_level_read`. Its historical device-ID label is misleading:
it loads the existing input-ready handle at `0x20006804`, clears only the low
byte of saved incoming R3, calls registry slot 0x10 with `(handle,0,&word,0)`,
and returns the byte independently of provider status. Callback changes to the
whole word are restored to R3. Existing ready/input ownership is reused.

`board/native_touch_identity.c` supplies native `0x5128c`. It retains the full
power/GPIO sequence and delays: acquire, 20, stop, high, low, 130, high, 10,
output close, 20, input open, then 40 before the first readiness read.
The counter begins at 100 and decrements before each read. A zero byte exits;
nonzero bytes trigger delay 2. There are at most 100 reads, including the final
count-zero read, and exhaustion leaves counter -1 after the last short delay.
The C signed counter is bounded to this range, so explicit 16-bit narrowing
is unnecessary and would make the examined compiler hold an extra register.

After polling, the routine opens the bus and uses the actual C request adapter
to read register zero, length two, into its private saved-word buffer. It then
calls delay 10, stop and the existing power step, and returns the buffer's low
byte. The initial low halfword is zero, high bytes are preserved, raw request
status does not replace the byte, and cleanup callback changes remain visible.
The full saved word is restored to R3.

The product passes 928 paired ready-reader cases and 2,592 complete-probe cases.
They cover every ready byte, untouched/byte/halfword/word effects, raw statuses,
null/ordinary/all-ones handles, early readiness, boundary reads 99/100 and
exhaustion, changing cached input handles, partial ID reads and late cleanup
mutations. Tests execute the actual C ready and request helpers, checking
provider calls/arguments, live R4–R11, signed counter states, delays, final R0/R3,
SP, masks and callback-cell guards. Seven wrong-owner/clear/Boolean/retry/delay/
register/cleanup variants are rejected.

Frame depths still differ: ready reader C16 versus native8; probe C24 versus
native16. Private buffer locations are normalized in comparisons. Qualification
admits neither entry, and no exact region is added. REA bytes also establish
that the probe's complete body includes the POP at `0x51308`, ending at
`0x5130a`; the working frontier size is corrected from 124 to 126. Historical
census evidence is retained unchanged.

All 588 R1 units compile with unchanged 164/34 import sets. The 586 unaffected
prior objects, prior request function bytes/relocations and shared request data
are unchanged. The source plan and canonical hybrid remain unchanged at 4,245
source-built bytes and the locked application hash. GPIO/power/delay and final
registry providers are modeled. Caller-clobbered registers/flags except R0/R3,
electrical behavior, actual timing, arbitrary aliases/faults/concurrency and
complete source-only rebuilding remain unproven. Probes, REA evidence and audit
are under `build/goal-r1-touch-identity-c`; durable results are in the adjacent JSON.
