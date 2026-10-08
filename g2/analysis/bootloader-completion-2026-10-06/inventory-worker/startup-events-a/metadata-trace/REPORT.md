# Stock event-A metadata trace

This trace uses the locked G2 2.2.6.10 image (`f89a4c…67b5`) and the complete
1,371-byte initializer at `0x20000000` (`e3bea7…b843`). The stock trace runner
decodes the authenticated compressed stream in Python and checks the complete
output digest before running original callback instructions. The comparison
runner separately executes the actual stock scatter decoder. Both preserve
the initializer's default state: major 7 at `0x20000150`, adjacent initialized word 7 at `0x20000148`,
TON 6 at `0x2000014c`, and last timer 255 at `0x20000154`. The callback table
at `0x20000158` is read from those decoded bytes. The fixture profile uses
their VDDC/VDDF rank words; its other packed fields are marked synthetic.

`trace_stock_default.py` first records a valid callback target and stops before
opaque stock instructions. The only callback allowed to execute after that
stop is selector 24, whose authenticated stock body is `BX LR`. The 254-case
receipt in `stock-default-sweep.json` covers six direct temperature fixtures,
eight other event IDs, and 240 combinations across five classifier outcomes,
CPU state, state flag, peripheral masks, and GPU auxiliary state.

The default temperature-0 fixture requests target major 5 from current major
7. The real stock walker calls selector 24 at `0x42a030` and then selector 16
at `0x42962c`. At selector 16, the observed caller return is `0x42a4b0`,
arguments are `[5, 7, 0, 6]`, PRIMASK is 1, and the installed state remains
major 7 / TON 6 / timer 255. Stock execution stops before selector 16's first
instruction. The 49.5 fixture reaches the same target and arguments; 50.0
requests major 4 and reaches the same selector IDs with `[4, 7, 0, 6]`.

Across the full sweep, the observed stock selector paths were:

| Path | Cases | Meaning |
| --- | ---: | --- |
| 24 → 16 | 106 | Verified no-op executes; stop at selector 16 |
| 24 | 10 | Verified no-op then callback returns |
| 24 → 3 | 38 | Stop at first opaque selector 3 |
| 3 | 38 | Stop at first opaque selector 3 |
| 24 → 2 | 2 | Stop at first opaque selector 2 |
| 2 | 2 | Stop at first opaque selector 2 |
| no callback | 58 | Callback returns without a table call |

Selectors 8 and 15 were not reached from initialized major 7 in these
fixtures. The actual frontier is earlier: selector 2 or 3 for several state
combinations, and selector 16 for the default temperature path. No success
return was supplied for any opaque stock callback.

`compare_default_native.py` provides a full source comparison against
`/tmp/opencfw-root-pcm22-relocated/record-candidate.elf` (SHA-256
`4b1fb7…10c645`). Stock uses the original decoder; source uses the candidate's
compiled-source scatter adapter. Both tables are checked against the
authenticated table, with source relocations validated against
`native-selector-bindings.json`; neither table is manually installed by the
harness. The comparison executes stock/source selector 24 and selector 16,
then returns through the full callback for 0.0, 49.5, and 50.0. Selector IDs,
entry arguments, uint32 status in R0, final SP, callee-saved registers, final
state, mutated args, and ordered MMIO writes match. State reaches major 5 for
0.0/49.5 and major 4 for 50.0. Caller-saved R1 differs: stock leaves
`0x20000144`, while source leaves `6`; this register is recorded and excluded
from the declared uint32 return contract. The default callback paths visit
178 of selector 16's 212 authenticated bytes; its TIMER_A branch is not taken.
The synthetic TIMER_A control is disabled and ROM address `0x40` is not called.
Peripheral register starting values are deterministic synthetic values, and
no hardware behavior is claimed.

Reproduce with the local Unicorn environment:

```sh
/Users/kalani/.local/share/opencfw/venv/bin/python \
  g2/analysis/bootloader-completion-2026-10-06/inventory-worker/startup-events-a/metadata-trace/trace_stock_default.py \
  --sweep --output g2/analysis/bootloader-completion-2026-10-06/inventory-worker/startup-events-a/metadata-trace/stock-default-sweep.json

/Users/kalani/.local/share/opencfw/venv/bin/python \
  g2/analysis/bootloader-completion-2026-10-06/inventory-worker/startup-events-a/metadata-trace/compare_default_native.py \
  --elf /tmp/opencfw-root-pcm22-relocated/record-candidate.elf \
  --output g2/analysis/bootloader-completion-2026-10-06/inventory-worker/startup-events-a/metadata-trace/default-native-comparison.json
```
