# QMA setup sequence in C

`r1_qma_setup` now uses ordinary C instead of naked assembly. Stock entry
`0x86ee4` and REA/Ghidra establish a fixed setup sequence that ignores all
helper return values and always returns one. No early abort, retry policy
or cleanup is added.

The sequence resets the device, writes `4a=20`, `50=51`, `56=01`, selects
range four, optionally writes the rate pair below, then writes `3e=87`,
`4a=28`, `20=05`, delays five units, writes `5f=80`, delays five, writes
`5f=00` and delays five. It finishes with steps enabled, any-motion
arguments `(0,1)` and tap arguments `(0x31,0,1)`.

| Full setup rate | Register `0x10` | Register `0x11` |
| --- | --- | --- |
| 25 | `0x00` | `0x86` |
| 50 | `0x06` | `0x84` |
| 100 | `0x01` | `0x85` |
| 150 or 200 | `0x02` | `0x85` |
| Other values | no write | no write |

There are 18 helper/write calls for recognized rates and 16 otherwise.
The existing range C body executes, including its four-byte scale store
of 1024 before register `0x0f` is written. The existing identity/layout
entry still truncates the rate to a byte before calling setup; direct
setup calls use the full value.

Stock/source comparison passes 2,328 scenarios: 1,164 direct setup calls
and 1,164 combined identity/layout calls. Coverage includes every byte
rate, high-word rate values, zero/nonzero/random helper returns, callback
mutations to state/default data, caller-saved flag/register clobbering,
and interrupt masks. Probes independently assert the complete call plan,
arguments, ignored failures and scale-store ordering, then compare ordered
state/default accesses, full state/guards, return values, callee-saved
registers, restored stack and masks. Callbacks require eight-byte alignment.

The C setup body is 200 bytes versus 194 stock bytes. The compiler also
regenerated the identity/layout caller using setup's invariant return of
one. The combined tests execute both actual C bodies and validate their
stock behavior; arbitrary replacement setup returns from the earlier
isolated review are outside this combined execution. All other helper
instruction bodies remain unchanged. Steps, any-motion and tap receive
proper C argument declarations; their assembly is retained.

All 562 R1 units compile without failures or duplicate strong symbols in
`build/sources-goal-r1-qma-setup/report.json`; imports remain 227 application
and 34 bootloader. Reset, register writes, delays and remaining sensor
helpers are modeled. Physical operation, timing, complete fault state,
final linking and byte identity remain unverified. No source-plan selection
or G2 workflow gate changed.

[Machine-readable evidence](qma-c-setup-review.json) binds source, manifest,
build/native hashes, REA observations and ignored probes under
`build/goal-r1-qma-setup/`.

The later [reset review](qma-c-reset-review.md) replaces the reset helper
with C while the setup and identity/layout instruction bodies remain unchanged.
