# NFC charge-task event policy correlation

## Decision

The explicit Ghidra seed at `0x000461CC` is a real R1 task-event handler, not
data inside one of Ghidra's broad noncontiguous bounding ranges. Its 662-byte
executable body is `0x000461CC..<0x00046462`, followed by its literal and
diagnostic island. The full envelope is `0x000461CC..<0x00046650`, ending at
the next native function. The full
1,156-byte envelope hashes to
`ed5a9b82902f050e4940ea199d8de22031802f7d7abc4cd3041e98a6590f19fc`;
the executable bytes hash to
`632f49d7a293f0826bc7d52e62ec21d06b1e35054424e80b5a79d054ff643a6f`.

The sole direct caller is the system task at `0x00092556`. The local
`r1_nfc_charge_task_plan_build` captures the handler as pure action intent.
It does not receive live task or device pointers and performs no provider
operation.

## Event masks and fixed actions

The stock handler tests independent bits in this order; multiple bits may be
handled in one pass.

| Mask | Recovered action intent |
| ---: | --- |
| `0x00000001` | set the existing charged-notification policy and open touch |
| `0x00000002` | run the standard-command IRQ sequence, write ST dynamic register `0x100B=1`, clear the field-seen state, schedule `0x800`, and open touch |
| `0x00000010` | run the not-charging sequence, clear battery charge latches, write `0x100B=0`, schedule `0x1000`, close touch, and validate temperature IDs |
| `0x00000004` | clear the existing charged-notification policy |
| `0x00000008` | dispatch the already bounded PMIC charge-event policy with value `0x5A` |
| `0x00000040` | report the charging battery percentage; when it is zero, request eight battery updates with a 10-tick delay after each |
| `0x00000020` | request one ordinary battery update |
| `0x00400000` | drain one 44-byte charge-task message record |
| `0x00800000` | release task synchronization, deregister watchdog slot one, then enter the terminal wait-forever path |

The standard-command and not-charging branches retain distinct action flags,
so a combined event does not collapse their ordered register writes or touch
transitions into one final state.

## Temperature-ID retry policy

The not-charging branch reads two provider ID bytes and accepts only exact
`50 50`. A successful first, second, or third attempt consumes respectively
one, two, or three reads and zero, one, or two 100-tick retry delays. Each
failed read is followed by the delay, including the third; therefore total
failure produces three reads and three delays before requesting the recovered
watchdog-reset action. The clean planner accepts all three ID pairs as bounded
observations and returns the read count, delay count, success attempt, and
reset intent.

## Provider boundary

ST25DVxxKC transport and GPO control remain with the pinned official ST
provider. Touch open/close, battery sampling, PMIC/YHM behavior, Nordic/CMSIS
queues, timers, watchdog/task lifecycle, and logging remain separately owned.
The planner neither implements nor calls any of them. The already admitted
PMIC charge-event and charged-notification planners remain independent source
boundaries rather than being duplicated here.

Host tests cover invalid API arguments, the combined non-destructive event
path, fixed values and delays, second-attempt temperature success, all-three
failure/reset, zero and nonzero battery percentages, and terminal task intent.

## Verification

```sh
python3 tools/evidence/summarize_r1_nfc_charge_task_policy.py
```

The summarizer pins the recovered application hash, full envelope, executable
body, sole caller, exact diagnostic strings, and representative ST, delay,
battery, temperature-ID, and PMIC callsites.
