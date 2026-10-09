# Current corrected source-ledger status

- [UART RX and PCM reconciliation](REPORT.md): named RX and variant bodies are
  already covered; stale pending rows are superseded.
- [UART instance wrapper](../audio-uart-instance-closure-2026-10-09/REPORT.md):
  16 new comparisons and exact static task configuration.
- [Earlier corrected successor](../source-ledger-successor-2026-10-09/INDEX.md):
  retain its resolved UART TX/INFO/PCM2.2 findings, but replace its UART RX and
  PCM0.7/2.0/2.1 pending rows with this reconciliation.

The enclosing common low-power initializer is already complete in
`audio-clock-reset-active-2026-10-08`. Next static targets are CPU power-mode
wrappers/callers and UART3 TX IRQ drain. Runtime callback registration, exception delivery,
calibration and physical behavior remain explicit external boundaries.
