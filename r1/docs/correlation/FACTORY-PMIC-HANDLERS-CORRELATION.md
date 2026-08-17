# Factory PMIC handlers correlation

## Decision

Three explicit Ghidra seeds are independent R1 eAT factory handlers selected
through the fixed command table. They are not members of the broad
noncontiguous functions whose bounding ranges happen to cover them.

| Command | Executable extent | Bytes | SHA-256 | Complete envelope |
| --- | --- | ---: | --- | --- |
| `AT^PMIC_ISNS` | `0x0004F4A4..<0x0004F4B6` | 18 | `63368b0d8baa9f979c34e43d8fcb22d62d9b3d406e628a5909a45434405e986b` | `0x0004F4A4..<0x0004F4D4`, 48 bytes, `a531e776e4f86cfaabb77ed89fc1e0638c004b0de1b51a44924624e907c3455b` |
| `AT^PMIC_OFF` | `0x0004F4D4..<0x0004F50C` | 56 | `2eb10962b78d9955ba18e7e248c54634961c3c0ed1c5a56b39559deca79076dc` | `0x0004F4D4..<0x0004F524`, 80 bytes, `854b9cd35972c89007c794b2cffc5db3cf2a0976d196a034fee1362df9f66733` |
| `AT^PMIC_READ` | `0x0004F524..<0x0004F57C` | 88 | `0c99a9668a257b387077589dcbc77e87c608c80e7dfaf5fea540bc463c03455c` | `0x0004F524..<0x0004F598`, 116 bytes, `aebf19ec25374940a9ec71d7e9b02e6f248ccda9c4094ded1bcc501a68a9b277` |

All three have zero direct branch callers. Their table records and Thumb
pointers are `0x000C4250`/`0x0004F4A5`, `0x000C4240`/`0x0004F4D5`, and
`0x000C4210`/`0x0004F525`, respectively.

## Recovered behavior

`AT^PMIC_ISNS` obtains the already converted current-sense millivolt value
from `0x000506A4`, formats that value, and returns one.
`r1_factory_pmic_current_diagnostic_plan_build` preserves the provider result
without sampling the ADC or emitting text.

`AT^PMIC_OFF` emits its diagnostic, obtains the battery millivolts and current
firmware timestamp, and constructs the `dev_info` power-recovery fields. The
low two bits are fixed action/state `2`; the next fourteen bits contain
`battery_mv & 0x3FFF`. It requests the existing `dev_info` setter and then
sets power-thread flag `1` before returning one. The clean
`r1_factory_pmic_power_off_plan_build` records the raw and masked voltage,
exact packed word, timestamp, persistence intent, and thread-signal intent.
It cannot perform either side effect and exposes no executor.

`AT^PMIC_READ` zeroes twelve stack bytes, invokes the branch-only YHM2710
register-9 one-byte veneer at `0x00050748`, and formats ten bytes from the
buffer. Consequently, the actual command output is register 9 followed by
nine zero bytes; it does **not** read registers 0 through 9. The clean
`r1_factory_pmic_register_diagnostic_plan_build` preserves this exact behavior.
This corrects the older capability-ledger interpretation that inferred a
ten-register hardware read from the ten-value format string.

Every handler returns the fixed value one. Tests cover raw current-sense
preservation, the 14-bit voltage mask, state bits, packed-word maximum,
timestamp and flag intent, the one-plus-nine register layout, and null output.

## Safety and provider boundary

No helper samples the ADC, operates the YHM2710 transport, reads time, writes
`kv.bin`, signals a thread, formats text, registers an eAT command, or turns
power off. In particular, `AT^PMIC_OFF` is represented only as an inert plan;
there is no callable destructive route in the source-built firmware API.

## Verification

```sh
python3 tools/evidence/summarize_r1_factory_pmic_handlers.py
```

The evidence script pins all three executable/envelope hashes, command-table
records, Thumb pointers, zero direct-call sets, exact strings and format
pointer, and every local provider/formatter/persistence/thread callsite.
