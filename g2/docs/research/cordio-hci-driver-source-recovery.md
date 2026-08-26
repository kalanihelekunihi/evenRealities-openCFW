# Ambiq Apollo3 Cordio HCI-driver recovery

Status date: 2026-08-25  
Target: G2 `s200_v2.2.6.10` Apollo main

## Current closure

The stock Apollo3 driver has 12 linked functions totaling 1,188 bytes and four
source-only APIs. Its main contiguous code interval is
`[0x004B48A6,0x004B4D2C)`, 1,158 bytes, SHA-256
`809a750836b2494d4d71125db43181e4f84f12333a07b2d4d8147ee59a9be983`.
The separate `error_check` helper is `[0x004B47AE,0x004B47CC)`. Concatenating
the 12 bodies in source order gives SHA-256
`82d378d8a979e3cede7a46f2d0c9027840afbeb931c42e3484acf15b6bde154a`.

The four source-only definitions are `HciDrvErrorHandlerSet`,
`HciVscConstantTransmission`, `HciVscCarrierWaveMode`, and
`HciDrvBleSleepSet`. `HciDrvIntService` is retained but unrooted: the complete
OTA vector table, direct-call scan, and stored-pointer scan contain no ingress
to it. The previous claim that its hardware-vector caller was outside the OTA
was incorrect. Vector slot 75 is present in the image and points to the
separate Apollo510 `GPIO0_607F` group handler at `0x004B80BE`; that handler
does not call `HciDrvIntService`. Any runtime ingress to the retained service
therefore remains unresolved and is not inferred.

The exact scan closes 30 direct calls into entries and all 66 direct calls
issued by linked bodies. The only stored entry is the intentional WSF handler
cell `0x004B8798 -> 0x004B4AB3`. Thirty aligned words in unrelated packed data
equal the numeric interior address `0x004B4B00`; none is accepted as a pointer.
There is no direct branch or accepted pointer into a strict function interior.

## Transport and state ABI

Stock uses the blocking Apollo3 path (`USE_NONBLOCKING_HCI=0`) with a ten-second
heartbeat. The TX queue at `0x20073BA8` owns eight 260-byte records backed by
`0x20065A10`; RX uses a 256-byte buffer at `0x20000DAC`. One handler invocation
allows at most 1,000 transactions and four consecutive reads.

The handler drains retained RX bytes into `hciTrSerialRxIncoming`, services
blocking BLEIF reads and writes, and restarts the heartbeat on activity. A
transport failure runs `error_check`, shuts down and boots the radio, empties
the write queue, and requests `DmDevReset`. Shutdown stops the heartbeat,
disables the BLE interrupt, powers down/deinitializes the controller, and
clears the read counters.

The shared pool `[0x004B4D2C,0x004B4DC4)` is 152 bytes, SHA-256
`ad18de8bc3c1e8d0d93235970032a5f454accb1f7ec00754cd246490ef5fb421`.
It identifies the BLE handle and status fields, queue and buffer storage,
heartbeat/wake timers, handler ID, BLE MAC, and the eight-byte NVDS command
buffer. It is a mixed-owner IAR pool and is not claimed as an exclusively owned
contiguous driver object.

## Mixed source lineage

No examined official file is an exact whole-file source match. The transport,
boot, and shutdown logic descend from the Ambiq Apollo3 driver. AmbiqSuite
R2.5.1 provides the historical baseline (blob
`02efb8c27f1138af998a53824c230d82bc611239`, SHA-256
`55bf59929abdcb3c1c39903a6f5e3c4806443b245e404e1616475388244664b4`).
The stock handler's null-message guard instead agrees with the later official
R3.1.1 Apollo3 import (blob `89cfb37c843f49d015adeada3619bc47aeed2a39`,
SHA-256 `246aaa2365ca175712209ddbb6b3544377934b41d347f878367a2363f8a4d0d2`).

The VSC tail uses still newer semantics: RF power opcode `0xFCC4`, BD-address
opcode `0xFC43`, and NVDS-update opcode `0xFFF2`. The official R4.4.1 Cooper
driver (blob `e767f925b6cf3de4d250d6965b3fe1931a3c1025`, SHA-256
`1f1461f0eeedc21277e9e9afb7dbdab2d7d89dbf101d1cc588e1ea220e06b7b0`)
is therefore a semantic oracle for these small helpers, not an Apollo3
transport oracle. `HciVscUpdateNvdsParam` also populates six product runtime
bytes before sending its eight-byte vendor payload.

The correct classification is a mixed-version Ambiq driver. These later
official imports corroborate reconstruction behavior; they are not asserted
to be G2's historical generating commit. The files carry Ambiq's
BSD-3-Clause-style notice. openCFW currently records hashes, ABI, and
clean-room behavior only; no vendor source bytes were copied into production.

The complete ledger is
[`ambiq-cordio-hci-driver-function-map.tsv`](../../tools/manifests/ambiq-cordio-hci-driver-function-map.tsv).
[`analyze_g2_cordio_hci_driver.py`](../../tools/analyze_g2_cordio_hci_driver.py)
pins that ledger, source provenance, aggregate closure, every body, the shared
pool, direct-call digests, state literals, and entry/interior classification.

## Clean-room implementation and hardware boundary

Project-original C now implements all 16 inventoried APIs and target-compiles
for Cortex-M55. Nine hardware-independent entries are production-routed:
`error_check`, `hciDrvWrite`, `HciDrvHandlerInit`, `HciDrvIntService`, the four
NVDS/RF-power/BD-address helpers, and `HciDrvEmptyWriteQueue`. They replace 368
stock bytes with 472 compiled bytes plus 14 alignment bytes under seven strict
relocations. Host tests cover queue ownership, bounded transfer/recovery,
address validation, callbacks, vendor payloads, and failure handling.

Six radio-controller operations remain hardware-evidence-blocked:
`HciDrvRadioBoot`, `HciDrvRadioShutdown`, `HciDrvHandler`,
`HciVscConstantTransmission`, `HciVscCarrierWaveMode`, and
`HciDrvBleSleepSet`. Their maintained implementations compile, but the live
stock paths are intentionally retained until authorized responsive G2/EM9305
hardware can provide boot, interrupt, timing, RF-test, and sleep evidence. No
hardware was available or accessed, so this document does not claim physical
validation.

Reproduce the software closure with `make cordio-hci-driver-closure`.
