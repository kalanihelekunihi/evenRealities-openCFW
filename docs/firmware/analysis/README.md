# Firmware Analysis

Deep analysis of Even G2 firmware internals, consolidated from dated investigation logs
into topical reference documents.

## Consolidated Analysis Documents

| Document | Scope |
|----------|-------|
| [firmware-version-analysis.md](firmware-version-analysis.md) | EVENOTA corpus across versions 2.0.1.14–2.0.7.16: per-version breakdown, component decomposition, header validation, integrity/packaging semantics |
| [hardware-artifact-characterization.md](hardware-artifact-characterization.md) | BLE artifact extraction (UUIDs, state markers, AT commands), hardware subsystem ownership map, cross-version behavior evolution |
| [startup-sequences.md](startup-sequences.md) | Boot call graphs for G2 main MCU, box/case MCU, and R1 ring. Init table effects, runtime entry chains, disassembly notes |
| [service-dispatch-architecture.md](service-dispatch-architecture.md) | Dispatch descriptor chains, root callback candidates, navigation/devinfo lanes, boxdetect/BLE chain, ring relay, system monitor call chains |
| [kernel-scheduler-architecture.md](kernel-scheduler-architecture.md) | FreeRTOS scheduler core semantics, OS wrapper layer, box scheduler task map, idle/wait call trees |
| [settings-protocol-architecture.md](settings-protocol-architecture.md) | Settings notification capture sweep, service correlation, device-status wrapper (case 4 map), callgraph resolution, root-case wrapper sweep |
| [sequence-replay-validation.md](sequence-replay-validation.md) | BLE capture replay assertions: packet timing, stream balance, sequence ordering thresholds |

## Cross-Cutting References

| Document | Scope |
|----------|-------|
| [firmware-string-cross-reference.md](firmware-string-cross-reference.md) | 34,866 unique firmware strings indexed and categorized |
| [tagged-artifacts.md](tagged-artifacts.md) | SHA-256 verified firmware artifact inventory (5 G2-Case + 3 R1-Ring) |
