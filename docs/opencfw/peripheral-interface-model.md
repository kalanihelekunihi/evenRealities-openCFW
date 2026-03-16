# Peripheral Interface Model

This document is the clean-room Apollo-side boundary map for subordinate firmware images, peer-glass synchronization, case relay, and ring integration.

`openCFW` should currently treat these as host and relay boundaries. Only the Apollo510b side is ready for direct implementation work; the subordinate images remain compatibility targets unless their state changes elsewhere in `openCFW/docs/`.

## Boundary Matrix

| Boundary | State | Transport | Surface / Artifact | Identified Today | Main Gaps | openCFW Posture |
|---|---|---|---|---|---|---|
| Apollo510b -> EM9305 | Identified | HCI | `firmware_ble_em9305.bin` | 4-record patch container, erase/write/reset order, Apollo BLE-host ownership | Function-level EM9305 patch semantics | Host adapter only |
| Apollo510b -> GX8002B | Identified | TinyFrame serial | `firmware_codec.bin` | FWPK wrapper, BINH stage1/stage2 boot, codec-host ownership | Full runtime command dictionary | Host adapter only |
| Apollo510b -> CY8C4046FNI | Identified | I2C | `firmware_touch.bin` | I2C DFU path, touch/prox ownership, versioned touch feature growth | Row grammar, thresholds, calibration tables | Host adapter only |
| Left eye <-> Right eye | Partial | Wired TinyFrame / `uart_sync` | Apollo runtime peer-sync path | Non-BLE inter-eye transport and master/slave shape are real | Exact frame taxonomy and final feature ownership split | Dedicated peer-sync layer |
| Apollo510b -> Case MCU | Partial | Wired UART with framing + CRC | `glasses_case`, `box_uart_mgr`, `firmware_box.bin` | Relay path, OTA forwarding, known `0x13` status and `0x58` OTA-check commands | Full opcode map and exact state machine | Relay compatibility first |
| Apollo510b <-> R1 ring domain | Partial | `0x91` relay + ring BLE (`BAE80001`, `FE59`) | G2 ring relay, ring direct runtime/DFU surfaces | `0x91` executable relay lane, ring runtime service family, Nordic DFU split | Full ring enums, direct command vocabulary, missing ring runtime image | Relay and compatibility only |

## Identified Boundaries

### Apollo510b -> EM9305 BLE radio

- Apollo owns the BLE host stack and application-visible GATT/ATT/GAP behavior.
- EM9305 is a subordinate radio and link-layer target programmed over HCI.
- The patch artifact is stable across the recovered G2 family, which makes the boundary more important than the internal EM9305 code path for `openCFW`.
- Clean-room implication: keep an explicit controller adapter and patch-loader abstraction instead of smearing radio bring-up into generic BLE service code.

### Apollo510b -> GX8002B audio codec

- Codec boot uses TinyFrame plus two BINH stages before runtime audio/control traffic starts.
- The codec boundary owns LC3-adjacent audio processing, wake-word handling, and voice-preprocess functions that do not need to be reimplemented inside the Apollo runtime first.
- Clean-room implication: `openCFW` should model a codec host driver with boot, command, stream, and error domains separated.

### Apollo510b -> CY8C4046FNI touch controller

- Touch and proximity sensing are offloaded to the Cypress sidecar.
- Apollo owns the host-side gesture integration and DFU/update path over I2C.
- Clean-room implication: keep touch/prox acquisition behind a device adapter and do not treat it as a pure protobuf-service concern.

## Partially Closed Boundaries

### Left/right peer-sync transport

- Inter-eye coordination is wired and TinyFrame-backed, not BLE.
- Runtime evidence points to a dedicated `uart_sync` thread and peer event forwarding path.
- The transport is real enough to enforce an architectural rule now: `openCFW` needs a first-class peer-sync module.
- Remaining gap: exact message families and the final left/right authority split are still incomplete.

### Case MCU relay

- The case is not a phone-visible BLE endpoint.
- G2 relays case traffic through `glasses_case` and `box_uart_mgr`, with framed UART traffic and CRC validation.
- Known command anchors include status/telemetry (`0x13`) and OTA check (`0x58`), and the case firmware itself now has startup and scheduler anchors.
- Remaining gap: the full UART opcode grammar and exact state transitions are still incomplete.

### Ring integration boundary

- The G2 runtime contains an executable `0x91` relay lane that forwards ring-oriented payloads.
- The ring itself exposes a separate Nordic-style runtime and DFU family (`BAE80001`, `FE59`, SMP/MCUmgr), which is not part of G2 EVENOTA.
- Clean-room implication: keep G2-side relay semantics and any future ring-direct client logic separate. A ring firmware rewrite is blocked until the standalone runtime image exists in the corpus.

## Unidentified and Blocked Areas

- Exact inter-eye TinyFrame frame schemas and per-message ownership.
- Full `box_uart_mgr` opcode table and case-state machine closure.
- Direct ring `BAE80001` proprietary command vocabulary.
- Full ring relay enum tables on `0x91`.
- Standalone R1 runtime image and its runtime call tree.
- Function-level EM9305 patch semantics.
- Steady-state codec host command/event dictionary after BINH boot.
- Touch-controller row/update grammar and calibration tables.

## Clean-Room Implementation Rules

- Implement Apollo-side host drivers first. Do not attempt subordinate firmware rewrites from partial evidence.
- Keep transport adapters separate by boundary: HCI, TinyFrame, I2C, UART, and ring relay/direct BLE.
- Treat peer-sync as its own module, not as a side effect of ordinary BLE service code.
- Gate case and ring features behind instrumentation until their grammar and enum tables close further.

## Source Documents

- `../firmware/ble-em9305.md`
- `../firmware/codec-gx8002b.md`
- `../firmware/touch-cy8c4046fni.md`
- `../firmware/box-case-mcu.md`
- `../firmware/device-boot-call-trees.md`
- `../firmware/firmware-communication-topology.md`
- `../firmware/g2-service-handler-index.md`
- `../firmware/re-gaps-tracker.md`
- `../devices/g2-glasses.md`
- `../devices/g2-case.md`
- `../devices/r1-ring.md`
