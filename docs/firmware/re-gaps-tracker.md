# Firmware RE Gaps Tracker

Date: 2026-03-05  
Scope: prioritized unresolved reverse-engineering gaps across G2-L/G2-R/G2-Case/R1.

Status legend:
- `OPEN`: unresolved
- `PARTIAL`: some evidence recovered, still ambiguous
- `BLOCKED`: missing artifact blocks closure

## Priority Queue

| Priority | Gap | Device(s) | Status | Current Evidence | Evidence Needed to Close |
|---|---|---|---|---|---|
| P0 | Main app reset-handler call graph (full symbolized startup) | G2-L/R | PARTIAL | bounded reset disassembly recovered (`0x005C9776 -> 0x005C9798 -> 0x005C97D8 -> 0x005B4088`), dynamic handoff point (`blx [0x20003DB4]`) identified, descriptor field accesses mapped (`+0x08/+0x1C`), worker-chain fan-out anchored (`0x0048719C -> 0x00486E02 -> 11 descriptor slots`), callback initialization confirmed (`[0x20003DB4 + 0x00] = 0x00487423`), post-dispatch chain anchored (`0x00487422 -> 0x004873F4 -> 0x0048719C`), stage2 idle-loop mechanics instruction-closed (`0x48723A/0x487240` wait/tick + backedges + descriptor waiter `0x486EA6/0x486EB8`), wrapper semantics promoted (`os_thread_create`/`os_event_wait_timeout`/`os_event_wait_ex`), and scheduler-core helper lift completed with cross-domain xrefs (`0x452*`/`0x453*` in `0x0044xxxx/0x004Cxxxx/0x004Dxxxx/0x0051xxxx`) | resolve RTOS-family-level symbol equivalence for helper internals (`0x441*`, `0x486*`, queue/list primitives) and map remaining unnamed runtime lanes to service/thread ownership |
| P0 | Ring ownership split (left/right/master/slave exact runtime authority) | G2-L/R + R1 | PARTIAL | mixed master/slave + right-eye-audio/ring capture hints | endpoint-labeled dual-eye+ring live traces with command origin attribution |
| P0 | Standalone R1 runtime firmware image RE | R1 | BLOCKED | FE59/SMP/MCUboot flow inferred; bundled Nordic DFU binaries now have confirmed reset/stage2/idle anchors (`0x000F83D8 -> 0x000F8200 -> 0x000FADC8/0x000FADBC`, init walker `0x000F84DE -> 0x000F84CE`, SoftDevice `wfe` loop `0x00025FDC <-> 0x00025FDE`), but no standalone ring app binary in corpus | ring application image dump/package + symbol/string extraction |
| P1 | EM9305 on-radio internals beyond patch-record table | G2-L/R | PARTIAL | NVM patch container fully decoded (4 records, 29 erase pages, FHDR at 0x302000, 210KB main patch at 0x302400), ISA corrected to ARC EM (ARCv2), 14 HCI VSC commands documented, hardware pinout mapped | ARC EM disassembler (MetaWare/nSIM/Ghidra ARC plugin) for function-level analysis |
| P1 | Service `0x08-20` exact handler/function mapping | G2-L/R | **RESOLVED** | `pb_service_navigation_handler` at `0x00589324` fully mapped (handler_map.txt session 8), 10+ sub-commands, protobuf schema decoded, all lanes symbolized | — |
| P1 | Service `0x09-*` device-info dispatch symbol map | G2-L/R | **RESOLVED** | `pb_service_device_info_handler` at `0x004aa906` mapped (function_map.txt), settings parser chain symbolized, all sub-commands identified | — |
| P1 | Unknown service `0x90-??` semantics | G2-L/R | OPEN | dispatch-table mention in services docs | traffic capture or symbol/xref proving function and packet schema |
| P1 | Ring relay enum tables (`command_id`, `event_id`, touch `type`) | G2-L/R + R1 | PARTIAL | service `0x91` descriptor slot and executable chain now anchored (`0x0067643C=0x91`, `0x005B46B0 -> 0x005B41FC`, send `0x005B46A4 -> 0x0046F5C4` with `r1=0x91`) plus parser diagnostics xrefs (`0x005B4370`, `0x005B43D8`, `0x005B44F0`, `0x005B473A`) | enum table extraction + capture correlation for each value |
| P1 | BLE advertising parity under controller pressure (`L/R/Ring` concurrent attach) | G2-L/R + R1 simulator | PARTIAL | simulator now includes adaptive multi-instance -> single-fallback ad mode with round-robin recovery probes | labeled concurrent iOS traces proving stable 3-endpoint connect/reconnect parity (success rate + latency envelope) |
| P2 | ALS brightness pipeline numeric transform (sensor->DAC->sync) | G2-L/R | PARTIAL | `ALSSyncHandler` strings + JBD brightness deprecation marker | conversion curve and write path recovery from ALS handlers |
| P2 | Case UART frame-level schema and command map | G2-Case | PARTIAL | `box_uart_mgr` + CRC/error + OTA markers recovered; G2-side BoxDetect dispatch/notify chain now anchored (`0x004B4714 -> 0x004B4526/0x004B44BE`, BLE send `0x004B451E -> 0x00463178` with `r0=0x81`, corrected handler/case-sync xrefs `0x00717798/0x007177B8`) | complete packet grammar (opcodes/fields/checksum coverage) |
| P2 | BoxDetect auxiliary callee semantics (`0x00545866 -> 0x00543E06`) | G2-L/R + G2-Case relay lane | OPEN | caller edge and dispatch-side case-sync message xref are anchored, but callee semantics are still unresolved and not yet linked to a confirmed case-UART parser | semantic lift of `0x00543E06` call tree + capture-backed correlation to case relay traffic |
| P2 | `/v2/g/check_firmware` successful contract | API/G2 update backend | OPEN | extensive probes still return `1401` | successful request contract with parameter/state requirements |

## Suggested Closure Order

1. Resolve RTOS-family-level symbol equivalence for scheduler internals (`0x441*`, `0x486*`, queue/list primitives) and map unnamed runtime lanes to specific service/thread ownership.
2. Collect endpoint-labeled dual-eye + ring captures, including ad-mode transition traces under controller pressure (closes ownership/ring enum and BLE fallback parity questions).
3. Acquire standalone R1 runtime firmware artifact (enables direct ring boot/runtime RE).
4. Decode remaining unresolved service `0x90-??` (services `0x08` and `0x09` now RESOLVED).
5. Deepen peripheral internals (EM9305 with ARC tooling, ALS brightness pipeline, case UART grammar).

## Cross-References

- Boot/call trees: `docs/firmware/device-boot-call-trees.md`
- Topology map: `docs/firmware/firmware-communication-topology.md`
- Service/offset index: `docs/firmware/g2-service-handler-index.md`
- Module-level backlog: `docs/firmware/g2-firmware-modules.md`
- Reset startup artifacts: `captures/firmware/analysis/2026-03-05-g2-reset-startup-callgraph.md`, `captures/firmware/analysis/2026-03-05-g2-reset-startup-disassembly-notes.md`, `captures/firmware/analysis/2026-03-05-g2-dispatch-descriptor-chain.md`, `captures/firmware/analysis/2026-03-05-g2-startup-init-table-effects.md`, `captures/firmware/analysis/2026-03-05-g2-runtime-entry-chain.md`, `captures/firmware/analysis/2026-03-05-g2-os-wrapper-semantics.md`, `captures/firmware/analysis/2026-03-05-g2-scheduler-core-semantics.md`, `captures/firmware/analysis/2026-03-05-g2-idle-wait-calltree.md`, `captures/firmware/analysis/2026-03-05-g2-dispatch-root-callback-candidate.md`
- Navigation / dev-config descriptor-adjacent artifact: `captures/firmware/analysis/2026-03-05-g2-nav-devinfo-descriptor-lanes.md`
- BoxDetect relay-chain artifact: `captures/firmware/analysis/2026-03-05-g2-boxdetect-ble-chain.md`
- Ring relay executable-chain artifact: `captures/firmware/analysis/2026-03-05-g2-ring-relay-callchain.md`
- System-monitor executable-chain artifact: `captures/firmware/analysis/2026-03-05-g2-system-monitor-callchain.md`
- Case startup artifacts: `captures/firmware/analysis/2026-03-05-box-reset-startup-callgraph.md`, `captures/firmware/analysis/2026-03-05-box-scheduler-task-map.md`
- R1 Nordic DFU startup artifacts: `captures/firmware/analysis/2026-03-05-r1-nordic-dfu-startup-chain.md`, `captures/firmware/analysis/2026-03-05-r1-nordic-stage2-idle-paths.md`
