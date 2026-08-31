# G2 hardware-evidence audit — 2026-08-30

Date: 2026-08-30 (America/Chicago)
Scope: read-only host inventory for the Apollo-main source-closure goal

No hardware operation was performed. This audit did not open a serial port,
connect over BLE, reset, flash, erase, sign, read device memory, or exercise a
G2 peripheral.

## Observed host state

- `system_profiler SPUSBDataType -json` returned no enumerated USB records.
- `/dev/cu.usbserial-210` and `/dev/tty.usbserial-210` are present, together
  with the generic macOS debug-console endpoints.
- The serial endpoint was not opened. Its presence alone does not supply a live
  G2 identity, current device state, owner authorization for this qualification
  run, or any behavioral evidence.
- No `JLinkExe`, `JLinkGDBServer`, `nrfjprog`, `pyocd`, `openocd`, `probe-rs`,
  `cargo-embed`, `nrfutil`, or `adafruit-nrfutil` executable was found on the
  active `PATH`.
- No current flash readback, INFO0/INFOC dump, BLE capture, UART transcript,
  logic-analyzer trace, power trace, audio capture, display observation, or
  independently observed peer interaction was supplied to this goal.

## Qualification status

Apollo-main hardware qualification is **blocked by unavailable physical
evidence**. Offline host tests, Cortex-M55 compilation, deterministic component
builds, package construction, and byte-accounting receipts are software
evidence only and must not be reported as live-device validation.

The historical authorized-device record and staged recovery constraints remain
in [`hardware-validation-2026-08-23.md`](hardware-validation-2026-08-23.md).
The current controlling rule remains
[`hardware-validation-policy.md`](hardware-validation-policy.md): no device
operation is implied by a build or source-admission goal, and the existence of
a serial node is not permission to use it.

## Evidence required to unblock

At minimum, a future qualification run must bind the responsive physical target
to the authorized G2 identity, record the exact candidate artifact and readback,
and collect capability-specific observations. Apollo-main gaps currently need,
as applicable, BLE/controller traces, paired-temple behavior, display output,
audio cadence and capture, filesystem persistence/power-loss behavior, sensor
timing, command-list/cache/power behavior, stack high-water marks, and WCET
measurements. Each result must be retained as a reproducible capture rather than
inferred from successful compilation or flashing transport.
