# Current static source-ledger successor

This index supersedes the residual rows in
`source-ledger-reconciliation-2026-10-09`.

## Newly closed

- [UART3 TX IRQ drain](../audio-uart3-tx-irq-drain-2026-10-09/REPORT.md):
  40 new compositions through actual channel IRQ and HAL service into the
  source-backed TX state machine and queue drain.
- [UART instance wrapper](../audio-uart-instance-closure-2026-10-09/REPORT.md):
  16 comparisons and exact static worker configuration.

## CPU power-mode attribution

The selected PCM2.2 transition corpus does not call a distinct public
`am_hal_pwrctrl_mcu_mode_select` wrapper. Its complete disassembly call census
contains delay/status, timer, cache and TON helpers; LP/HP request, ACK polling,
temporary HFRC2 force and domain changes are macro-expanded inline in the
already recovered transition bodies. All 27 table bodies, including these
inline mode changes, are covered by `audio-transition-producers-closure-2026-10-08`.

Pinned Ambiq `am_hal_pwrctrl.c` remains useful for enum names and intended
software sequence, but it is not evidence that a separate stock wrapper body
was linked or called by this family. No exact caller or diagnostic symbol binds
the public wrapper to a remaining locked address. Inventing such a binding
would duplicate inline coverage and misattribute bytes.

## Remaining boundaries

For the requested audio/UART/power ledger, remaining claims require one of:

- live vector/NVIC/PendSV and task-selection traces;
- authentic calibration, INFO1 and runtime callback-table contents;
- physical UART/GPIO/clock/power observations;
- private/proprietary source or authenticated resident ROM for previously
  documented unavailable families.

Other firmware subsystems still contain static reconstruction work, so this is
not a whole-image source-complete declaration. No additional public dependency
download is useful for these residuals: the official Ambiq source is already
pinned, and missing evidence is runtime state, private source, ROM, or
first-party application code. The unmatched duplicate Ambiq gitlink remains
recorded and untouched.
