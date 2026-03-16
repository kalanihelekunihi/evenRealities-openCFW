# Diagnostics and Observability Model

This document is the clean-room model for diagnostics, monitoring, crash artifacts, and debug-surface behavior in the G2 runtime.

## Diagnostics Matrix

| Domain | State | Main Evidence | Identified Constraints | Remaining Gaps |
|---|---|---|---|---|
| Logger control plane | Identified | logger module, service map, firmware strings | `0x0F` is a dedicated logger service with file-list, delete, delete-all, and live-control families; `/log/` is an explicit namespace guard | exact live payloads, exact heartbeat/status fields |
| File export over file lane | Partial | file-transfer module, logger module, services doc | file lane supports a separate glasses-to-phone export direction distinct from normal send flow | exact export command bytes, retry semantics, result-check behavior |
| Crash and rotating log artifacts | Identified | device storage notes, firmware RE, logger evidence | `/log/compress_log_*.bin` and `/log/hardfault.txt` are stable runtime artifacts; hardfault log has a bounded rotation rule | exact compression format, full retention policy |
| System monitor lane | Partial but executable | `0xFF` callchain, topology notes, boot-call trees | `0xFF` is a real dedicated handler path tied to runtime monitor and idle signaling | full command table, nested payload schema, event timing |
| AT or CLI debug shell | Identified with bounded unknowns | G2 device docs, S200 main-image notes, firmware RE | FreeRTOS CLI and AT families exist for BLE, sensors, display, filesystem, and teleprompter-adjacent control | exact grammar, transport path, build gating |
| Live log streaming | Partial | app RE logger notes, logger module | logger control extends beyond static file management and includes live enable/level semantics | exact on-wire payloads, category filters, transport sink |
| Lab-only debug and production-test operations | Partial | CLI evidence, source-tree notes, gray-screen discovery | flash-write and production-test surfaces exist and are implementation-relevant as hazards | exact privilege boundaries and safe reproduction rules |

## Identified Diagnostics Contracts

### Logger Is a Dedicated Service With a Namespace Guard

- `0x0F` is a dedicated logger control plane, not a generic file helper.
- Known command families include:
  - file list
  - delete file
  - delete all
  - live switch
  - live level
  - heartbeat
- Firmware explicitly validates that mutable logger paths must start with `/log/`.
- Clean-room parity should preserve that prefix guard rather than allowing arbitrary filesystem mutation through the logger plane.

### The File Lane Is Bidirectional

- The shared file lane on `0x7401/0x7402` is not only for phone-to-glasses sends.
- A separate glasses-to-phone export direction exists for:
  - diagnostic logs
  - crash artifacts
  - other captured data
- Clean-room parity should therefore keep send and export as separate subprotocols even though both ride the same `0xC4/0xC5` lane family.

### Crash and Log Artifacts Are Stable Compatibility Objects

- Observed stable runtime objects include:
  - `/log/compress_log_0.bin` through `/log/compress_log_4.bin`
  - `/log/hardfault.txt`
- Device-level notes also preserve left-eye and right-eye path separation (`L:/` and `R:/`) around the same log namespace.
- `hardfault.txt` has a bounded size rule in the recovered evidence and rotates or truncates rather than growing without limit.

### SystemMonitor Is a Dedicated Monitor Path

- `0xFF` is bound to `system_monitor_common_data_handler`.
- The executable chain closes a real notify sender and a scheduler-idle marker.
- That makes `0xFF` implementation-relevant even before the full payload schema is closed, because it is part of runtime health and steady-state observability rather than a synthetic test hook.

### A Debug Shell Exists Outside the Phone-Facing App Protocol

- The firmware exposes FreeRTOS CLI and AT command families for:
  - system info and reset
  - BLE and EM9305 control
  - IMU and ALS reads
  - brightness and screen control
  - audio controls
  - teleprompter-adjacent commands
  - LittleFS file operations
- These are real firmware contracts, but they are not the same thing as the phone-visible BLE feature protocols and should not be mirrored blindly into normal runtime UX paths.

## Inferred Diagnostics Behavior

### Logger Live Mode Is Richer Than Simple ACKs

- App RE and logger command families strongly suggest live logging has:
  - enable or disable state
  - level control
  - some category or sink selection
- The clean-room implication is that logger live mode should remain instrumentation-first until packet captures close the actual envelope format.

### SystemMonitor Carries More Than One Idle Ping

- Topology and service notes indicate monitor responsibilities that likely include:
  - peer reboot coordination
  - display-running or app-running status
  - scheduler or idle-state reporting
- The executable call chain proves the lane is real, but not yet the full event vocabulary.

### Debug Shell and BLE Features Overlap Operationally

- Commands such as brightness, teleprompter, BLE control, file access, and sensor reads have both shell-facing and runtime-service-facing evidence.
- The clean-room implication is that `openCFW` should treat shell surfaces as privileged adapters over lower-level subsystems rather than as the canonical public API.

### High-Risk Debug Operations Are Probably Lab-Only

- `file2xip`, `xip2file`, gray-screen production test, and raw reflash-style commands indicate firmware capabilities beyond normal user-facing behavior.
- These should be treated as lab or manufacturing surfaces until transport, privilege, and safety boundaries are better closed.

## Unidentified Areas

- Exact logger export command bytes and result-check semantics on `0xC4`.
- Exact logger live-stream payload schema, category filters, and output sink.
- Exact `0xFF` command and event vocabulary, including nested appId fields.
- Exact mapping from shell commands to BLE or internal subsystem calls.
- Exact AT/CLI transport, authentication, and build-gating rules.
- Exact compression format and retention policy for `compress_log_*.bin`.
- Exact privilege boundary for XIP read or write, production gray-screen, and other manufacturing-style commands.

## Clean-Room Rules

- Keep logger, export, and system-monitor logic as a dedicated diagnostics plane.
- Preserve the `/log/` namespace guard.
- Keep file send and file export as separate subprotocols on the shared file lane.
- Gate high-risk shell or production-test operations behind lab-only build or runtime controls.
- Treat `0xFF` as a typed observability lane, not a generic event bus.
- Keep unresolved logger live-stream and system-monitor fields behind instrumentation rather than freezing speculative schemas.

## Source Documents

- `../devices/g2-glasses.md`
- `../firmware/s200-firmware-ota.md`
- `../firmware/firmware-reverse-engineering.md`
- `../firmware/g2-firmware-modules.md`
- `../firmware/firmware-communication-topology.md`
- `../firmware/device-boot-call-trees.md`
- `../firmware/modules/logger.md`
- `../firmware/modules/file-transfer.md`
- `../firmware/g2-service-handler-index.md`
- `../protocols/services.md`
- `../firmware/analysis/2026-03-05-g2-system-monitor-callchain.md`
