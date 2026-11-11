# R1 PPG and touch line power control in C

Six stock entry points now compile from
`r1/src/application/board/native_peripheral_line_power.c`, with no inline
assembly and no new handle storage. They use the existing owners populated
by `r1_led_ldo_device_bind`: `r1_led_enable_device` at `0x20007688` and
`r1_touch_ldo_device` at `0x2000768c`.

REA and raw Thumb instructions establish the following contracts:

| Stock entry | C candidate | Behavior |
| --- | --- | --- |
| `0x50304` | `r1_peripheral_line_release` | Select line 0/1; slot 18 with words 0,0; reload handle; slot 0c |
| `0x50338` | `r1_peripheral_line_acquire` | Select line 0/1; slot 08; reload handle; slot 18 with words 1,0 |
| `0x5036c` | `r1_goodix_transport_release` | Release line 0 |
| `0x50372` | `r1_goodix_transport_prepare` | Acquire line 0 |
| `0x50378` | `r1_touch_bus_enable_on` | Release line 1 |
| `0x5037e` | `r1_touch_bus_acquire_on` | Acquire line 1 |

Line 0 is `ppg_led_en`; line 1 is `touch_ldo_en`. Historical source/frontier
labels do not establish electrical behavior. In particular, the historical
touch `enable_on` name points to the release helper. The two selectors are
compared as full words; all values other than zero and one return without
loading either cached handle. Operation statuses are ignored as stock does.

Each operation uses a fresh volatile handle load. A first operation may change
the selected cell through a callback; the second operation must see that
change. The implementation retains this behavior rather than caching the
device pointer. The four wrappers force their native selector regardless of
incoming argument registers.

The ignored probe `build/goal-r1-peripheral-line-power/verify.py` passes
15,552 paired cases (31,104 executions). Actual stock and reconstructed
registry dispatchers execute; final device callbacks are modeled. Cases cross
six entries, six full-word selectors, null/A/B handles in each cell, every
presence mask for slots 08/0c/18, callback mutations to another device or null,
and operation success/error. Comparison covers handle-load ordering, operation
arguments, final handle memory, callee-saved registers, stack restoration and
interrupt masks. Void return residue and private stack bytes are excluded.

A deliberate C mutation that hoists the selected handle before the first
operation is rejected: release on device A, whose slot-18 callback replaces
the cell with B, incorrectly closes A instead of B. This provides a concrete
negative check of the callback-order coverage.

The full R1 report `build/sources-goal-r1-peripheral-line-power/report.json`
compiles 564 units with no failures or duplicate strong symbols; imports
remain 210 application and 34 bootloader. `make sources-check` passes.
[Machine evidence](peripheral-line-c-power-review.json) records source,
verifier, REA snapshot, build report and manifest hashes.

These are behavioral candidates. The canonical source plan remains unchanged;
instruction identity and final source placement are unproven. Physical GPIO
and power sequencing, invalid record/table fault paths, concurrency and full
firmware integration are outside the bounded execution evidence. G2 workflow
gates remain unchanged.
