# Task suspend policy correlation

## Outcome

Two executable routines that Ghidra exposed only as explicit analysis seeds are now bounded manual
provenance supplements and represented by independently compiled pure C plans. No stock bytes,
thread handles, CMSIS implementation, or live suspension control are present in the source API.

| Extent | Bytes | SHA-256 | Source plan |
| --- | ---: | --- | --- |
| `0x00046D10..<0x00046DCC` | 188 | `27aaed8b4c2f758025abee09a50088b081b72de1e49188f0385f398683f845b1` | `r1_task_suspend_broadcast_plan_build` |
| `0x00046DCC..<0x00046E64` | 152 | `9147a124d72ca9559e39ce1df6ef9dbbb964486f1487c83fc3a57d0126709cc6` | `r1_task_suspend_barrier_plan_build` |

The first routine is called at `0x00046BF2`. It sends thread flag `0x00800000` in normal group
order `5,0,7,1,9,2,3,10,4` and returns the exact acknowledgment mask `0x06BF`. Configuration byte
`0x55` substitutes factory group 6 for normal group 5, producing order
`6,0,7,1,9,2,3,10,4` and mask `0x06DF`.

The second routine is called at `0x00045DB8`. It invokes the existing per-thread synchronization
helper `0x00046A74` nine times in order `0,1,2,3,10,7,5,9,4`; factory mode substitutes group 6
for group 5. The helper sends the same suspend flag and waits for `1 << group` with raw timeout
`0x5000`. The clean-room barrier plan records that ordered contract without calling the helper.

`python3 tools/evidence/summarize_r1_task_suspend_policy.py` hash-gates both bodies, their sole direct
callers, all ten state-block literals in each function, nine CMSIS flag calls, nine helper calls,
and both configuration-byte reads against the rebuilt application image.

## Boundary

These are product orchestration policies, not a CMSIS-RTOS reconstruction. Source callers must
bind the returned group/action data to a transparent scheduler they own. The plans cannot discover
stock handles, signal a thread, wait on an event object, or suspend a running device by themselves.
