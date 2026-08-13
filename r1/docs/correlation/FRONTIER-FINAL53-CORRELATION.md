# Final-53 ownership residue correlation

This closure routes 53 functions. The last 53 previously unclassified application functions (1,548 declared body bytes; 1,406
range-pinned, 142 remote continuation bytes recorded as omitted) are now source-routed. After
this closure, **zero application or bootloader entries remain unclassified** in the ownership
ledger. Residual risk lives in the documented provider boundaries, not in anonymous code.

| Family | Functions |
| --- | ---: |
| GoMore licensed-provider candidate | 21 |
| Generic device-registry candidate | 10 |
| Goodix GH3X2X candidate | 9 |
| Nordic nRF5 SDK 17.1.0 | 4 |
| R1 product-specific | 4 |
| RTC-device provider candidate | 3 |
| Shared quantized-neural runtime candidate | 1 |
| FreeRTOS 10.5.1 Nordic port | 1 |

## Exact upstream closures

- `0x0009566C` is FreeRTOS 10.5.1 `tasks.c::uxTaskGetNumberOfTasks`: the six-byte
  `uxCurrentNumberOfTasks` getter. Its only callers are the exact-matched
  `xQueueGenericSendFromISR`, `xQueueGiveFromISR`, and `xQueueReceiveFromISR`, which use the
  return value as the `cTxLock`/`cRxLock` cap inside the `prvIncrementQueueTxLock`/
  `prvIncrementQueueRxLock` macros with the `queueINT8_MAX` (`0x7F`) `configASSERT` — an exact
  function-local match against the authenticated kernel snapshot, not an R1 patch.
- `0x00034410` is `modules/nrfx/drivers/src/prs/nrfx_prs.c` `nrfx_prs_box_4_irq_handler`: the
  `PRS_BOX_DEFINE` body jumping through the box-4 handler record; box 4 is UARTE0
  (`0x40002000`), corroborated by the exact-matched sibling `prs_box_get`. It occupies the
  UARTE0 vector slot.
- `0x0005C034` is `components/ble/peer_manager/gatt_cache_manager.c::db_update_pending_handle`:
  `nrf_mtx_trylock` on the update-in-progress mutex, `local_db_update_in_evt`, and the
  unlock-on-failure path, with the ROM iterator-table pointer proving registration.
- `0x00034A7C` is `modules/nrfx/drivers/src/nrfx_wdt.c::nrfx_wdt_irq_handler`:
  `EVENTS_TIMEOUT` (`0x40010100`) check, installed-handler call, event clear. The stock vector
  table routes this body at the CCM_AAR slot while the WDT slot points at the Nordic SysTick
  handler — vendor board wiring, documented here without asserting its intent.
- `0x00093960` is legacy `integration/nrfx/legacy/nrf_drv_twi.c::twi_evt_handler`, installed by
  the exact-matched `nrf_drv_twi_init`.

## R1 product closures

Four small product bodies: the `fw_wtd` watchdog operation handler at `0x0006623E` (ROM
name/ops-table plus AT^ command strings), the GXT310-adjacent scaled register read glue at
`0x0006F80C` (R1-authored glue; the GXCAS provider gate itself is unchanged), the boolean
adapter `0x00096A40` (ownership from its sole R1 caller), and the six-byte helper `0x0003E8AE`.

## Blocked candidate closures with documented evidence limits

Ten generic device-registry candidates include the list link helpers `0x00077E30`/`0x00077E3C`
shared by the pinned registry insert/remove and the orphan-record operation wrappers. Twenty-one
GoMore candidates cover the sleep/temperature seam mathematics and the two-byte no-op hook
`0x00091080` called from the gated reinit path. Nine Goodix candidates include the heap
destructor `0x0003E6B0` and windowed-access helpers. Three RTC-device candidates and one shared
quantized-neural runtime member round out the residue. Every candidate entry remains
`investigate_before_implementing` or `vendor_source_required_not_redistributable` — no provider
internals, framework engines, or licensed algorithms are recreated.

Functions where the reading is fragile are explicitly listed in the residue notes: the
callerless GoMore/R1 seam quartet (`0x0004AA98`, `0x0004AAC0`, `0x0004B560`, `0x0004B598`) and
the GoMore block trio adjacent to the R1 touch configuration (`0x00072420`, `0x0007260C`,
`0x0008ED10`). Their dispositions are conservative provider gates either way; no entry claims
product authorship without product evidence.

Reproduce with:

```sh
python3 tools/evidence/summarize_r1_frontier_final53.py
python3 tools/build_r1_source_ownership.py --check
python3 tools/verify_openr1.py
```
