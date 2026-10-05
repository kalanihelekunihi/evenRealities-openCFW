# Local priority plan

User direction: **EvenHub SDK and similar application logic last.** This plan owns only the assessment task; it does not overwrite shared campaign assignments.

1. **P0 — Boot chain / reset / vectors:** Reset reachability and initialization ownership for every image; constructor/ISR scheduling contracts
2. **P0 — Memory / allocator / DMA / MPU-cache:** Pool/heap lifetime, DMA/copy boundaries, allocation failures, IRQ/cache coherence
3. **P0 — RTOS / tick / task / queues / ISR:** Multi-task due batches, future deadlines, critical section/inter-read mutation, actual interrupt delivery
4. **P1 — Apollo ↔ EM9305 / BLE host-controller:** HCI enqueue/copy/ownership, controller records, RF sequencing and host↔controller failure recovery
5. **P1 — Apollo ↔ codec / audio hardware:** Reset/start/stop/DFU handshakes, PCM timing/metadata producer, frame faults and DMA buffer ownership
6. **P1 — Apollo ↔ touch:** Command/report layout, IRQ/attention ordering, power transitions, calibration and resident-loader boundary
7. **P1 — Apollo ↔ charging case:** Frame/resync/checksum, bank swap, charger/watchdog buses and disconnect behavior
8. **P1 — Temples ↔ each other:** Synchronization state ownership, framing/CRC, retransmission and device-role boot configuration
9. **P1 — Display hardware / draw buffers:** Panel command/register sequences, framebuffer stride/format, GPU ownership/cache/DMA and scanout lifecycle
10. **P1 — NOR / filesystem / persistent update:** Flash transaction state, erase/program safety, filesystem recovery, authenticated image install boundaries
11. **P1 — Sensors / power / board configuration:** Board variant dispatch, register transactions, IRQ/power timing, sensing↔scheduler interactions
12. **P1 — Security / crypto / update trust:** Trust boundary and recovery paths using synthetic inputs; no credential/device access
13. **P2 — G2 ↔ R1 ring transport:** Finish transport/lifecycle contracts before app actions; R1firmware is a separate locked artifact, not these six payloads
14. **LAST — EvenHub / SDK / product feature services:** Defer new work until foundations/buses/drivers/IPC contracts reviewed; retain interfaces needed to explain hardware consumers

Coordination: active state assignments are stale relative to current120xxRTOS fixtures. The parent/coordinator must identify those writers and communicate this priority order before reserving overlapping functions. If the coordinator confirms an active RTOS owner, keep that bounded work intact. Artifact timestamps alone do not establish a live worker. No shared state/gate/queue was edited, and no new decompilation worker was launched by this assessment.
