# G2 dashboard watchface-manager recovery

Status: read-only, fail-closed closure of stock 2.2.6.10
`app\gui\dashboard\dashboard_watchface_manager.c`.

## Result

The single 98-byte baseline path anchor expands to the complete physical
object `[0x00500410,0x00500824)`: 17 functions / 956 instruction bytes plus
an 88-byte terminal compiler pool, for 1,044 physical bytes. Baseline Ghidra
defined nine functions; recursive control-flow, exact entry edges, and the
stored selector pointer recover the other eight. All 415 instructions, 34
direct calls, 15 register-indirect calls, 24 image-wide direct entry sites,
one stored entry pointer, adjacent boundaries, and the absence of interior or
unknown direct targets are pinned.

The object selects one of four operation tables for watchface kinds 1 through
4. Each table is 15 words / 60 bytes. Kinds 1 and 2 implement all 15 slots,
kind 3 implements 11, and kind 4 implements nine; every non-null slot is an
odd Thumb pointer to an in-image first-party watchface function. Slot zero
creates a layout, slot `0x04` deinitializes it, and the remaining manager
wrappers guard and forward slots `0x08` through `0x38`. The exact battery
setter forwards slot `0x18`. Unknown kinds produce a null operations table;
nonzero layout-create results are logged and converted to a null layout.

## Dependency result

No third-party implementation is embedded. Thirty direct calls are
EasyLogger diagnostics at the admitted 2.2.99 source-equivalent selected
commit `a596b264…`. The only other direct external call reaches a bounded
six-byte first-party dashboard-state getter. All 15 indirect calls terminate
through the four pinned first-party watchface tables. There are no direct
CMSIS-FreeRTOS or FreeRTOS calls, no new dependency family, and no new version
discriminator.

The private historical source and producing commit remain unavailable, so
the eight offset-only wrapper names are semantic labels rather than recovered
source spellings. Individual watchface implementations remain separate
first-party objects. The manager is not production-routed.

## Reproduction

```sh
make dashboard-watchface-manager-closure
```

The target performs authenticated read-only analysis and tests only.
