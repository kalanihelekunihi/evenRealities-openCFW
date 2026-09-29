# G2 protocols (s200_v2.2.6.10)

Consolidated from the legacy G2 research record before its removal. Every
fact cites the file it came from; paths are repository-relative and remain
reachable through git history after deletion. Nothing here was observed on
the wire: all facts come from static analysis of the authenticated official
payloads. Addresses are Apollo-main run addresses (`run = file_offset +
0x00437FE0`) unless stated otherwise.

Confidence vocabulary:

| Level | Meaning |
|---|---|
| Proven | Byte-level fact pinned against the authenticated image: a table, constant, string, record, or exact instruction sequence. |
| Strong | Behavior recovered from the machine code and consistent across objects, but never captured on a live link. |
| Inferred | Derived by interpretation or cross-reference; plausible but not directly pinned. |
| Unverified | Hypothesis, open gap, or contradicted/partial evidence. |

Abbreviations for frequently cited directories: `R/` = `g2/docs/research/`,
`M/` = `g2/tools/manifests/`, `C/` = `g2/components/`.

## 1. Link topology

| Link | Physical / carrier | Protocol stack | Confidence | Source |
|---|---|---|---|---|
| Phone <-> temple | BLE, EM9305 controller, Cordio host on Apollo | GATT profiles EUS/ESS/EFS/NUS/OTA -> `0xAA` multipart transport -> service ID -> nanopb service or file/OTA engine | Strong | `R/g2-ble-transport-profiles-recovery.md`, `R/g2-transport-protocol-recovery.md` |
| Temple (central) <-> R1 ring | BLE, G2 as central/client | product 128-bit service, three notify/write handles; ring commands | Strong | `R/g2-ble-ota-ring-profiles-recovery.md`, `R/g2-app-ble-central-recovery.md` |
| Temple <-> Apple ANCS | BLE, G2 as ANCS client | AmbiqSuite ANCC profile + 9 G2-local functions | Strong | `R/ambiqsuite-ancc-profile-source-recovery.md` |
| Left <-> right temple | UART (`uart_sync.c`) | TinyFrame v1.3.0 lineage, sync framework, multipart listeners | Strong (UART + TinyFrame); Inferred (inter-temple wiring) | `R/g2-uart-sync-recovery.md`, `R/tinyframe-wire-format-recovery-audit.md` |
| Temple <-> charging case | UART, STM32G0B1 USART1 on the case | `5A A5 FF <len>` frames, 8-bit additive sum | Strong | `R/g2-box-function-map-recovery.md`, `R/g2-box-uart-mgr-recovery.md` |
| Apollo <-> EM9305 | Ambiq HCI driver (Apollo3-derived, blocking BLEIF-style read/write) | HCI H4 packet types over the driver; vendor reset/NVDS chain | Strong (packet layer); Unverified (physical bus) | `R/cordio-hci-driver-source-recovery.md`, `R/cordio-hci-tr-source-recovery.md` |
| Apollo <-> GX8002 codec | UART3 (control, DFU) + I2S (audio, DMA) | `BUXX` command frames; NationalChip UART boot/`serialdown` for DFU | Strong | `R/g2-service-codec-host-recovery.md`, `R/g2-service-codec-dfu-recovery.md`, `R/g2-drv-gx8002b-recovery.md` |
| Apollo <-> touch (PSoC 4000T) | I2C, touch is SCB1 slave; GPIO attention line | 9-slot one-byte command set + 16-byte reports; DFU frames `01 cmd len .. 17` | Strong | `R/g2-touch-i2c-protocol-recovery.md`, `R/g2-service-touch-dfu-recovery.md` |
| Factory / production test | BLE NUS (`5A A5 7F` request) and case UART | `pt_protocol_procsr.c` 66-command dispatcher | Strong | `R/g2-thread-ble-production-dependency-boundary.md`, `R/g2-pt-protocol-procsr-dependency-boundary.md` |
| Debug console | UART console, FreeRTOS+CLI | 76 CLI commands incl. `AT^...` aliases | Proven (registration list) | `R/freertos-cli-console-task-source-candidate-audit.md` |

Naming note: in this firmware `pt` means **product test**
(`platform\product_test\pt_protocol_procsr.c`), not phone transport. The
phone transport is `platform\protocols\transport_protocol\transport_protocol.c`.

## 2. BLE GATT (phone-facing)

### 2.1 Product services (Cordio application adapters)

| Profile | Retained path | Stock interval | App event | Provider handle | Confidence | Source |
|---|---|---|---|---|---|---|
| OTA (AMOTA-derived) | under `platform\ble\profiles` | `[0x004BDB90,0x004BDE4C)` | `0xA0` reset, `0xA1` disconnect after 200 units, `0xA7` send | `0x0824` | Proven | `R/g2-ble-ota-ring-profiles-recovery.md` |
| EUS | `platform\ble\profiles\eus\profile_eus.c` | `[0x004BDE4C,0x004BE228)` | `0xA8` | `0x0844` | Proven | `R/g2-ble-transport-profiles-recovery.md` |
| ESS | `platform\ble\profiles\ess\profile_ess.c` | `[0x004BE228,0x004BE3A4)` | `0xA9` | `0x0864` | Proven | same |
| EFS | `platform\ble\profiles\efs\profile_efs.c` | `[0x004BE3A4,0x004BE6F0)` | `0xAA` | `0x0884` | Proven | same |
| NUS | `platform\ble\profiles\nus\profile_nus.c` | `[0x004BE6F0,0x004BEA04)` | `0xAB` | `0x08A4` | Proven | same |
| Ring client | under `platform\ble\profiles` | `[0x004C46C0,0x004C4CEC)` | `0xAC` notify via discovered TX handle | discovered | Proven | `R/g2-ble-ota-ring-profiles-recovery.md` |

Shared adapter behavior (Strong, `R/g2-ble-transport-profiles-recovery.md`):
4-byte control block {connection ID, handler ID, CCC-enabled, connection-ready};
event `0x12` connection readiness, `0x14` CCC state, `0x27`/`0x28` open/close;
module event allocates a 12-byte WSF message and sends through its provider
handle. The OTA write callback `APP_EvenOtaWriteCback` forwards to the Even OTA
provider (`R/g2-ble-ota-ring-profiles-recovery.md`). NUS is not the Nordic NUS
API; no public source matches EUS/ESS/EFS/NUS (Proven negative search, same doc).

**Gap (Unverified):** the 128-bit service and characteristic UUIDs of the Even
EUS/ESS/EFS/NUS/OTA services are not recorded anywhere in the legacy evidence.
They must be read from the GATT attribute tables during pseudocode review.
Cordio constant UUID objects: `att_uuid.c` constants at `[0x0078F53A,0x0078F550)`
(11 two-byte UUIDs); ATT base UUID copy in SRAM `[0x2000044C,0x2000045C)`
(Proven, `g2/docs/memory-map.md` Cordio ATT sections).

### 2.2 Stack parameters and startup

| Fact | Value | Confidence | Source |
|---|---|---|---|
| Host ACL RX limit | `HciSetMaxRxAclLen(251)` | Proven | `R/g2-app-ble-startup-recovery.md` |
| Peer ATT MTU floor | 247 | Proven | `g2/docs/functional-capability-ledger.md` (atts_proc row) |
| WSF buffer pool | `WsfBufInit(0x2940, 0x2004FA98, 4, 0x200003B0)` (10,560 B, 4 pools) | Proven | `R/g2-app-ble-startup-recovery.md` |
| WSF handler order | HCI, DM, L2CAP, ATT, SMP, app, product BLE, HCI driver | Strong | same |
| Startup | CCB init, radio shutdown, 100 us, radio boot mode 0, stack init, register, `DmDevReset`, delayed start callback `0x004B758B` after 10,000 ms | Strong | same |
| BLE address getter | returns SRAM `0x200737BF` (6 octets) | Proven | same |
| CCC set | six-entry table at `0x007518C0` | Proven | same |
| Delayed-start event | product event `0xBC`; rearm 10 s, 20 s after alloc failure | Strong | same |
| Advertising | product-test: indefinite fast; normal: fast 30 s then slow; adv data carries PSN, FW `2.2.6.10`, product version, name, address | Strong | `R/g2-app-ble-peripheral-recovery.md` |
| Peripheral app events | `0xAD`, `0xB5`, `0xB6`, `0xB7` | Proven | same |
| Discovery start event | `0xA5`; callback states 0..8 (DB hash, security, GATT, Ring, optional ANCS, config, handle report) | Strong | `R/g2-app-ble-discovery-recovery.md` |
| Connection params | fast event `0xA3`, slow `0xA4`, app request `0xB9`; fast/slow split at 25 and 72 units; conn IDs 1..3; 2/4/10/30/60 s delays; ESS and OTA force fast | Strong | `R/g2-app-connect-params-recovery.md` |
| Central (RingLink) messages | `0xAE`..`0xB4` connect, disconnect, cancel, unpair, scan, RSSI, PHY | Strong | `R/g2-app-ble-central-recovery.md` |
| Security | Cordio SMP legacy + LE Secure Connections, both roles; `pSmpCfg` -> `0x00774D44` | Strong | `R/g2-app-ble-startup-recovery.md`, SMP rows of the capability ledger |

## 3. Phone transport (`0xAA` multipart)

Object `transport_protocol.c` `[0x004B892C,0x004B9A80)`, 13 functions
(`TPL_Init` `0x004B892C`, `TPL_ReceivePacket` `0x004B910C`, `TPL_SendPacket`
`0x004B9640`, `TPL_RxPacketTimeoutHandler` `0x004B8DA2`, `_tplReponse`
`0x004B9012`). Distinct from TinyFrame: zero edges into the TinyFrame interval
(Proven, `R/g2-transport-protocol-recovery.md`).

| Byte | Field | Confidence |
|---|---|---|
| 0 | magic `0xAA` | Proven |
| 1 | source (low nibble), destination (high nibble) | Strong |
| 2 | sequence / sync byte (sender uses tick count) | Strong |
| 3 | fragment data length; final fragment includes the 2-byte CRC | Proven |
| 4 | total fragment count (>= 1) | Strong |
| 5 | fragment number, 1-based, <= total | Strong |
| 6 | service ID (protobuf service, or file/OTA command `0xC0`..`0xC7`) | Strong |
| 7 | flags: bit0 response-requested on send; bits1..4 status in responses; bit5 selects synchronous receive path | Strong |
| 8.. | data | Proven |

Rules (Strong unless noted; `R/g2-transport-protocol-recovery.md`, byte layout
from the reconstruction in `C/apollo_main/core_overlay/transport_protocol.c`):
- CRC-16/CCITT-FALSE (poly `0x1021`, init `0xFFFF`, MSB-first, no final XOR) over
  the whole unfragmented payload, stored little-endian after the final
  fragment; leaf at `0x0049ACD4` (Proven).
- Max payload `0x1000`; fragment capacity = current BLE payload capacity - 11.
- Send takes a CMSIS mutex (100 ticks), copies to a static 4 KiB buffer.
- RX keeps four 0x38-byte reassembly contexts keyed by service/sequence/
  source/destination/pipe, a packet bitmap for duplicate suppression, and one
  shared 1,500 ms timeout (`_rxNextPacketTimeout` posts WSF event `0xB8`).
- Response is an 8-byte header built from template `0x0078EC74` with status in
  byte 7; timeout responds with status 3. Header-only (`len == 0`, 8 bytes)
  frames are accepted as control.
- Stable across firmware versions: the same 13 functions occur in the prior
  firmware shifted by `+0x1E53C` (Strong).

## 4. Protobuf services (nanopb)

All services use route 1 on the protobuf BLE transmit/notify wrappers. Common
status codes: 2 = null input, `0x2B` = nanopb decode/encode failure, 0 =
success (unless noted). Services 5, 6, `0x0B`, `0x30` suppress a repeated RX
magic byte within 3,000 ms (status 13) and use 6/5 for null/decode failure.
Notify-type envelopes use `last_rx_magic + 1` without writing it back.
nanopb runtime is 0.4.9-compatible (commit `98bf4db6`, `R/g2-sync-info-dependency-boundary.md`).
Source for each row: `R/g2-pb-service-<name>-recovery.md`.

| Svc | Source file | Object interval | Message / buffer | Commands (cmd/tag) | Conf. |
|---|---|---|---|---|---|
| `0x04` | `pb_service_notification.c` | `[0x004D6BA8,0x004D798C)` | 76 B @`0x200F60E0`; buf `0x2037C7A0` | 1/3 notification control; 2/4 app-not-whitelisted (notify, two bounded strings); 3/6 whitelist control; 4/7 whitelist check (cache fail -> status 1/err 7, CRC equal -> 2/0, differ -> 3/0); other -> `0xA1`/5 | Proven |
| `0x05` | `pb_service_translate.c` | `[0x0059F53C,0x0059FAE0)` | 0x854 B @`0x200F9EE4`; buf `0x2037CAA0` | subtypes 5 notify, 6 mode switch, 7 command response; master-role gated | Proven |
| `0x06` | `pb_service_teleprompt.c` | `[0x005885B4,0x00588D74)` | 0xF58 B @`0x200F873C`; buf `0x2037C9A0` | `0xA6`/12 resp (1 B); `0xA1`/7 status (u16); `0xA2`/8 file-list req; `0xA3`/9 file select (66 B); `0xA4`/10 page-data req (u32); `0xA5`/11 scroll sync (12 B) | Proven |
| `0x07` | `pb_service_even_ai.c` | `[0x004E31CC,0x004E54C8)` | 0x20C B @`0x200F5884`; buf `0x2037C4A0` | (1,3) control, (2,4) VAD, (3,5) ask, (4,6) analyse, (5,7) reply, (6,8) skill, (7,9) prompt, (8,10) event, (9,11) heartbeat, (10,13) config; `0xA1`/12 resp; RX payload lengths 2,2,0x208,1,0x208,0x10C,2,2,2,4; duplicate magic rejected with status 1 (no time window) | Proven |
| `0x09` | `pb_service_setting.c` | `[0x0049B198,0x0049C070)` | 104 B; buf `0x200706EC`; descriptor `0x0077772C` | 1 response; 2/4 full status (brightness, L/R version, head-up, battery/charging, silent, unread); 3/5 recalibration (sel 1) / silent mode (sel 2); notify magic `0x2007486C`; duplicate 32-bit magic suppressed | Proven |
| `0x0B` | `pb_service_conversate.c` | `[0x005B1B4C,0x005B22BC)` | 0xFAC B @`0x200F4808`; buf `0x2037C2A0` | `0xA1`/9 notify (u16); 2/4 prep-note list req; 4/6 prep-note select; `0xA2`/10 resp; `0xA3`/12 tag tracking (12 B) | Proven |
| `0x0C` | `pb_service_quicklist.c` | `[0x0055894C,0x005597F0)` | 0x1238 B RX @`0x200F624C`, TX @`0x200F7484`; buf 0x400 @`0x2037A5A0` | 1/3 item; 2/4 multi-item (0xE8-B records); 3/5 event (1,2); notify seq `0x20074FFD` | Proven |
| `0x0E` | `pb_service_health.c` | `[0x0055A558,0x0055B2A4)` | 0x31C B @`0x200F5DC4`; buf `0x2037C6A0` | 1/3 single data; 2/4 multi data; 3/5 single highlight; 4/6 multi highlight (max 3 records fit) | Proven |
| `0x10` | `pb_service_onboarding.c` | `[0x004A78D0,0x004A8560)` | 16 B RX/TX; buf `0x200F612C` | 1/3 config; 2/4 heartbeat (0 ready else 8); 3/5 event; notify seq `0x20074FFB` | Proven |
| `0x30` | `pb_service_terminal.c` | `[0x005CE7C4,0x005CF2B4)` | 0x850 B @`0x200F9694`; buf 0x878 @`0x20374378` | `0xF0`/13 resp; `0xA1`/9 status; `0xA2`/10 voice input; `0xA3`/11 query reply; `0xA4`/12 interrupt (firmware symbol `APP_PbTerminalTxEncodeAgentInterrupt`); `0xA5`/18 session switch; `0xA6`/19 new session; `0xA7`/20 display state; `0xA8`/22 new-session cancel; `0xA9`/24 list focus; `0xAA`/25 overlay focus | Proven |
| `0x80` | `pb_service_dev_config.c` | `[0x004D83D8,0x004D8F4C)` | 0xD0 B @`0x200F57B4`; buf `0x2037C3A0` | dispatcher: 4 auth, 5 pipe-role, 6 ring-connect info, 7 BLE params, 8 disconnect, 9 unpair, 10 error code (resp tag 9), 11 set dev info, 12 get dev info, 13 factory restore, 14 heartbeat (30 s timer), 15 quick restart, 128 time sync, 129 audio control; unknown -> error 8 | Proven |
| `0x80` | `pb_service_pair_mgr.c` | `[0x004BB3DC,0x004BD054)` | 0x1A8-B notify objects | 4/3 security auth; 5/4 pipe role; 6/5 ring-connect info; 7/6 BLE params; 8/7 disconnect; 9/8 unpair (6-B ring MAC) | Proven |
| `0x80` | `pb_service_dev_setting.c` | `[0x00542DC4,0x00543C48)` | caller-owned | `0x0D`/`0x0C` factory restore; `0x0E`/`0x0D` heartbeat; `0x0F`/`0x0E` quick restart; `0x80`/`0x80` time sync {u32 utc, i8 tz} cached @`0x20004394`; `0x81`/`0x81` audio control (accepted no-op) | Proven |
| `0x81` | `pb_service_glasses_case.c` | `[0x00510A0C,0x00510FD8)` | 10 B RX @`0x200F5A90`, TX @`0x200F5A9C`; buf `0x2037C5A0` | cmd 1, payload sel 3: battery, charging, lid, glasses-present, error at bytes 4..8; notify seq `0x20074FFA` | Proven |
| `0x91` | `pb_service_ring.c` | `[0x005CE1DC,0x005CE7C4)` | 64 B RX @`0x200F86BC`, TX @`0x200F86FC`; buf `0x2037C8A0` | cmd 1 ring event {u16 MAC count, <=6 MAC bytes, u8 event ID (1 supported), u32 param}; relay record `0x006A45B0` -> `0x005CE691` | Proven |

Aggregate: 15 retained `platform\protocols\pb_service_*` paths, 143 linked
functions / 47,644 body bytes (`R/g2-pb-service-pair-mgr-recovery.md`,
`M/g2-pb-service-complete-closure.tsv`). The `.proto` schemas themselves are
not recovered; field layouts above are in-memory struct layouts (Inferred for
wire field numbers beyond the cmd/tag pairs).

## 5. File (EFS) and OTA transfer engines

Both reuse the `0xAA` 8-byte header; byte 6 carries the command. Transport
CRC is CRC-16/CCITT-FALSE; receive timeout 1,500 ms; buffer 0x1020 B
(Strong; `R/g2-ota-transport-dependency-boundary.md`,
`R/g2-efs-transport-dependency-boundary.md`, reconstruction in
`C/apollo_main/core_overlay/ota_transport.c`).

| Cmd | Engine | Meaning | Confidence | Source |
|---|---|---|---|---|
| `0xC0` | OTA | import/control: sub 0 start, 1 continue/activate, 2 result check, 3 export cancel | Proven | `R/g2-ota-service-recovery.md` |
| `0xC1` | OTA | raw import data; fixed status notifications LE `0x0402`, `0x0302`, `0x0502` | Proven | same |
| `0xC2`/`0xC3` | OTA | export control / export data | Proven | same |
| `0xC4` | EFS | import control (same subcommand set) | Proven | `R/g2-efs-service-recovery.md` |
| `0xC5` | EFS | import raw data; fixed payloads `{1,4}`, `{1,2}`, `{1,5}` | Proven | same |
| `0xC6`/`0xC7` | EFS | export control / data | Proven | same |

OTA service (`[0x004448F4,0x004488EC)`, 25 functions; `_evenOtaReplyToAPP`,
`_fileCmdParse`, `_fileRawDataParse`, `_verifyFlashContent`,
`_evenOtaBootloaderWriteFile2MRAM`, `_RPC_SystemOtaStatusSync`,
`OTA_SetInterface`): replies `{subcommand,status}` unless the interface is
UART; recognizes `ota/s200_firmware_ota.bin`, `ota/s200_bootloader.bin`,
fonts, touch, codec, EM9305, case, generic and external-flash images; backends
MRAM, filesystem, external XIP flash; 4 KiB sectors/chunks, CRC check and
read-after-write verify; transfer state 0x70 B, export state 0x60 B
(Strong, `R/g2-ota-service-recovery.md`).

EFS service (`[0x00456722,0x00458DF0)`, 12 functions): shared 0x78-B transfer
object @`0x20071CC8` (handle, 80-B path, type, size, CRCs, chunk length,
totals, progress, isStart); import buffer `0x2035BE08`, export buffer
`0x2035ADF8` (4 KiB each). Import types: 0 notification whitelist, 1 Android
message JSON (<= `0x2137` B), 2 logger file, 3 tracepoint file (2 and 3
rejected on import), `0xAA` arbitrary file. Completion checks size and
non-reflected CRC-32C. Export streams logger/tracepoint files in 4 KiB chunks
(Strong, `R/g2-efs-service-recovery.md`).

## 6. Update / DFU chain

| Step | Mechanism | Confidence | Source |
|---|---|---|---|
| Package | EVENOTA: magic `EVENOTA\0`, count, build date/time/version (16 B each), TOC at `0x40` (16-B entries: id, offset, size, CRC), trailer `evenota\0`+8 zero, 128-B component headers (magic `0x4E455645`, type ID, storage type, filename), payload CRC-32C non-reflected (MSB-first) | Proven | `g2/tools/open_cfw.py`, `g2/docs/memory-map.md` |
| Component order / type IDs | codec 4, EM9305 5, touch 3, case 6, bootloader 1, main 0 | Proven | `g2/docs/memory-map.md` |
| Main payload | 32-B preamble: word0 = flags `0x04` in bits 31..24 plus 24-bit total size, word1 = zlib CRC-32 of bytes 8.., `0xCB` type, run base `0x00438000`; installed from offset `0x20` | Proven | `g2/tools/open_cfw.py` |
| Update flag | 16-B record at `0x007FE000`, bootloader-owned | Proven | `g2/docs/memory-map.md` |
| Phone -> temple | OTA BLE profile -> `0xAA` transport `0xC0`/`0xC1` -> `ota_service` writes files/MRAM/XIP | Strong | section 5 |
| Bootloader DFU task | `[0x0042DE58,0x0042E104)`: read 32-B image header, CRC check `[0x0042D890,0x0042D9F0)` (24-bit size mask, skip 8-B header, table CRC), program `[0x0042DAE8,0x0042DC90)` (skip 32-B header, chunked program + compare via indirect callback), normalize vector base to `0x00438000`, validate SRAM stack vector, hand off | Strong | `R/g2-bootloader-dfu-*-source-closure.md` |
| Touch DFU | see section 9 | Strong | `R/g2-service-touch-dfu-recovery.md` |
| Codec DFU | see section 8 | Strong | `R/g2-service-codec-dfu-recovery.md` |
| Case DFU | see section 7 | Strong | `R/g2-case-uart-update-source-closure.md` |
| EM9305 DFU | `service_em9305_dfu.c` `[0x0052F442,0x0052FF4C)`, 7 functions: firmware file streaming, DFU state/status, chunk buffers, first-party transport dispatch; no direct Packetcraft calls. Wire format not recovered | Unverified (wire) | `R/g2-service-em9305-dfu-recovery.md` |
| Rollback | Apollo application update is single-slot; no proven autonomous rollback | Strong | `g2/docs/functional-capability-ledger.md` (Deployment) |

## 7. Glasses <-> charging case (UART)

Case side: STM32G0B1-class, USART1 is the only interrupt-driven USART, no DMA
(Strong, `R/g2-box-stm32g0-platform-recovery.md`). Glasses side:
`platform\device_mgr\box_uart_mgr.c` `[0x00539E92,0x0053A414)`, log tags
`[box_uart_mgr]` (pack/unpack, CRC, flush, start/stop, `pt cmd execute err`)
(Proven, `R/g2-box-uart-mgr-recovery.md`).

| Element | Value | Confidence | Source |
|---|---|---|---|
| Frame | `5A A5 FF <len> <payload...> <sum>`; header searched in first 4 RX bytes; byte 3 = length | Proven | `R/g2-box-function-map-recovery.md` |
| Frame check | 8-bit additive sum seeded with `len - 2` over `len` bytes, compared to `payload[len]` (`gls_frame_validate_dispatch` `0x08001E94`). No polynomial CRC in the case image | Strong | same; supersedes the "bit-wise CRC" reading in `R/g2-box-stm32g0-platform-recovery.md` |
| Channels | two symmetric packers (left/right) at `0x08008FA8`/`0x08009004`; write retried (stock loop 1..9 per `R/g2-case-uart-update-source-closure.md`; 10 per platform audit); exhaustion fills buffer with `0xFF` | Strong / Unverified (exact count) | both |
| RX parser | header/length/data state machine with staged timeouts; plain and `[noctrl]` variants (control vs non-control port) | Strong | `R/g2-box-stm32g0-platform-recovery.md` |
| Commands | `0x13` case->glasses status push (battery/hall/USB/charging change); `0x58` OTA offer/check; `0x5A` nested chunk checksum; `0x3D`/`0x3E` aging-exit ack | Strong | `R/g2-box-stm32g0-platform-recovery.md`, `R/g2-case-uart-update-source-closure.md` |
| Status telemetry | `{"vol","pct","open","usb","cur","GLS_L","GLS_R","temp"}` JSON log | Proven (string) | `R/g2-box-stm32g0-platform-recovery.md` |
| Glasses-side state | box-detect accessors `0x004AC726`, `0x004AC73C`, `0x004AC752`, `0x004ACAD0` feed pb service `0x81` | Strong | same, `R/g2-pb-service-glasses-case-recovery.md` |
| Case OTA | offer `0x58` + version compare (`1.x.y`, current 1.2.57) -> both temples ready -> running bank -> erase 128 x 2 KiB pages of inactive bank -> copy serial windows -> receive image with per-chunk check -> program doublewords -> 32-bit additive sum of big-endian words -> inform glasses -> option-byte `nSWAP_BANK` swap + reset | Strong | same, `g2/docs/memory-map.md` |
| Preserved windows | `0x0803F000..0x0803F00F`, `0x0803F800..0x0803F807`, `0x0807F000..0x0807F00F`, `0x0807F800..0x0807F807` | Proven | `g2/docs/memory-map.md` |
| Case wrapper | `EVEN`, version (3 B + 0), BE size, BE additive word sum, 16 zero bytes | Proven | `g2/tools/open_cfw.py` |

## 8. Apollo <-> GX8002 codec

| Element | Value | Confidence | Source |
|---|---|---|---|
| Control frame | magic ASCII `BUXX`; 14-B header {magic 4, cmd u16, seq u8 (@`0x20075013`), flags u8, body len u16, header CRC-32 over bytes 0..9}; body <= 16 B; optional 4-B body CRC by flag | Proven | `R/g2-service-codec-host-recovery.md` |
| Control UART | 115,200 baud; blocking read of header then remainder; 3 retries | Strong | same |
| Commands | `0x02` read version, `0x07` beamforming mode, `0x08` wakeup mode, `0x0B` mic gain, `0x0C` DMIC open, `0x0D` DMIC close, `0x0E` 1-bit mic delay (fixed frame `425558580e0101000000d4db2f68`), `0x0F` I2S output, `0x70` query mic state; async `GX8002_GetVoiceEvent` | Proven | same |
| Audio | I2S via Ambiq `am_hal_i2s` (AmbiqSuite 5.1.0), DMA double buffer, ISR in `drv_gx8002b.c` `[0x0057A46C,0x0057A900)` | Strong | `R/g2-drv-gx8002b-recovery.md` |
| DFU package | `/firmware/codec.bin` FWPK: 16-B header (`FWPK`, version, count) + 16-B records {type, size, offset, CRC-32 (zlib)}; type 1 boot image, type 2 main | Proven | `R/g2-service-codec-dfu-recovery.md`, `R/g2-codec-fwpk-segments-recovery.md` |
| DFU sequence | UART 230,400; send `0xEF`, wait `M`; stage 1: `0x59` + LE config word count, config in <=256-B chunks, wait `wfb`/`OK`, `GET` at 1,000,000 baud, `OK`; stage 2: `0x53` + raw LE checksum + size, wait `ready`, 256-B chunks, accept `O` + `boot>`; flash: `serialdown 0 <size> 8192` + seeded CRC-32, wait `~sta~`, <=8 KiB chunks with `~fin~`/`~sta~`, final `[Result]:`/`SUCC`; timeouts mostly 10 s | Strong | `R/g2-service-codec-dfu-recovery.md` |
| Boot header | >= 32 B; four BE fields at offsets 8, 12, 16, 20 | Proven | same |
| Upgrade check | `SVC_CodecCheckAndUpgrade(force)`: version query 200 ms timeout; skip if equal unless forced | Strong | same |

## 9. Apollo <-> touch controller (PSoC 4000T, I2C)

Touch payload is linked at flash `0x3300` (payload offset + `0x3300` = linked
address); this corrects the earlier base-0 model and relocates the "resident"
tables into the shipped payload (Proven, `R/g2-touch-relocated-vector-and-code-partition.md`).
Addresses below are payload offsets.

| Element | Value | Confidence | Source |
|---|---|---|---|
| Transport | SCB1 `0x40250000` I2C slave, IRQ7; RX buf `0x200009A0` 16 B, TX buf `0x200009B0` 16 B (idle fill `0x5A`); frame length 1..16 | Proven | `R/g2-touch-i2c-protocol-recovery.md` |
| Attention | GPIO PRT4 pin 0 active-low: assert via `0x40040444`, release via `0x40040440` after host read | Proven | same |
| Dispatch | `cmd = rx[0]`, `cmd <= 8`, table at linked `0xB0C4` (payload `0x7DC4`) | Proven | same + relocation doc |
| Reply | `[0]` reply ID, `[1]` status (0 ok / `0xFF` err), `[2]` `0x17` | Proven | same |
| Commands (slot order inferred) | 0 `0x0446` version (2.2.0.1, protocol word `0x01000202`); 1 `0x0466` read proximity baseline; 2 `0x0480` read long-press threshold; 3 `0x04A0` save baseline (deferred); 4 `0x04C8` write gesture config (u16, 0 rejected); 5 `0x052C` enter DFU (mailbox `[0x20000000]`, `AIRCR=0x05FA0004`); 6 `0x054C` read sensor report (10 B); 7..8 no body | Proven (bodies) / Inferred (slot indices) | `M/g2-touch-i2c-command-map.tsv` |
| Event report | 16 B @`0x20000990`: [0] event type, [1..3] payload, [4..5] baseline, [6..7] channel, [8..9] proximity, [10..11] gesture result; report timeout 640 | Proven | `R/g2-touch-i2c-protocol-recovery.md` |
| Config persistence | EEPROM emulation magic `UNVE` (`0x45564E55`); baseline saved when change > 49 | Proven | same |
| Host DFU frame | `01 <cmd> <len u16 LE> <payload <=32> <sum16> 17`; sum = 16-bit two's-complement additive over header+payload; replies <= 15 B; 100 retries | Proven | `R/g2-service-touch-dfu-recovery.md` |
| Host DFU commands | `0x38` enter, `0x4C` set app metadata, `0x37` send 32-B packet, `0x49` program block (4 packets = 128 B), `0x31` verify, `0x3B` exit | Proven | same |
| DFU package | `/firmware/touch.bin` FWPK, record type 3; programmed length = record size - 4 (trailing CRC-32C reflected) | Proven | same, `g2/tools/open_cfw.py` |
| Device-side DFU engine | not in the shipped payload; entered by mailbox + reset | Unverified (location) | `R/g2-touch-i2c-protocol-recovery.md` |

## 10. Apollo <-> EM9305 (HCI)

| Element | Value | Confidence | Source |
|---|---|---|---|
| Driver | Ambiq Apollo3-derived blocking driver (`USE_NONBLOCKING_HCI=0`), 10 s heartbeat; TX queue 8 x 260 B @`0x20073BA8` (store `0x20065A10`), RX 256 B @`0x20000DAC`; <= 1,000 transactions / 4 reads per call | Strong | `R/cordio-hci-driver-source-recovery.md` |
| Failure recovery | `error_check`, radio shutdown + boot, flush queue, `DmDevReset` | Strong | same |
| Transport | `hciTrSendCmd` type 1, `hciTrSendAclData` type 2; RX accepts type 4 events (2-B header, <= 255) and type 2 ACL (4-B header, <= `HciGetMaxRxAclLen`) | Proven | `R/cordio-hci-tr-source-recovery.md` |
| Vendor commands | NVDS update `0xFFF2`, RF power `0xFCC4` (param 6), BD address `0xFC43` | Proven | `R/cordio-hci-driver-source-recovery.md`, `R/cordio-hci-vs-reset-sequence-recovery.md` |
| Reset chain | Reset `0x0C03` -> NVDS `0xFFF2` -> RF power -> event masks (std, LE, page 2) -> address, buffers, states, whitelist, features, resolving list, max data length -> four LE Rand -> ready | Strong | `R/cordio-hci-vs-reset-sequence-recovery.md` |
| Interrupt | `HciDrvIntService` `[0x004B4A98,0x004B4AB2)` has no static ingress; vector 75 is `GPIO0_607F` (`0x004B80BE`) | Proven | `R/g2-app-ble-startup-recovery.md` |
| Physical bus | not established by the legacy evidence | Unverified | - |

## 11. Temple <-> temple sync (TinyFrame)

| Element | Value | Confidence | Source |
|---|---|---|---|
| Frame | SOF `0x01`, ID u16 BE, LEN u16 BE, TYPE u16 BE, HEAD_CKSUM u16, DATA, DATA_CKSUM u16 (only if LEN > 0) | Proven | `R/tinyframe-wire-format-recovery-audit.md` |
| Checksum | CRC-16/ARC (reflected `0xA001`, init 0, no xorout); table `0x006C0950`; head checksum includes SOF | Proven | same |
| Config | `TF_MAX_PAYLOAD_RX 0x6000`, parser timeout 100 ticks, 128 ID / 32 type / 10 generic listeners | Proven | same |
| Library | MightyPork/TinyFrame core blobs from `eb75483e` (identical through `a29167a6`); multipart helpers `TF_Query_Multipart` `0x00492266`, `TF_Multipart_Payload` `0x00492278`, `TF_Multipart_Close` `0x00492280` | Proven | `R/tinyframe-send-version-recovery-audit.md` |
| UART worker | `uart_sync.c` `[0x00541790,0x00541AF8)`: 24,576-B RX stream, events bit1 RX drain / bit2 send queue / bit4 TF tick; <=32 chunks of 1 KiB per wake; fixed 6-B handshake; product-mode branch reads a 10-B handshake | Strong | `R/g2-uart-sync-recovery.md` |
| Framework | `sync_framework.c` `[0x0045A578,0x0045EC7C)`, master/slave listeners, ten multipart handler pairs; `sync_interface_api.c` `[0x004646F0,0x00466010)` | Strong | `R/g2-sync-framework-recovery.md`, `R/g2-sync-interface-api-recovery.md` |
| Service records | ring battery: type 5 update / type 6 peer request under ID `0x105` | Strong | `R/g2-service-ring-battery-recovery.md` |
| Topology | left/right temple peer link (master/slave roles) | Inferred | same docs |

## 12. R1 ring link (as seen from G2)

| Element | Value | Confidence | Source |
|---|---|---|---|
| Role | G2 is BLE central; `app_ble_central.c` `[0x0049F828,0x004A35B0)` | Proven | `R/g2-app-ble-central-recovery.md` |
| RingLink states | IDLE, OPENING, CONNECTED, LOCAL_DISCONNECTING, SWITCH_DISCONNECTING, CANCELLING, UNPAIRING | Proven | same |
| Policy | owner by dominant hand and role; short/escalating/long retry; scene reconnect at 500/1000 ms; `ring_connect_policy.c` `[0x0049F020,0x0049F828)` with `RING_CONNECT_INFO` throttling | Strong | same, `R/g2-ring-connect-policy-dependency-boundary.md` |
| GATT client | discover a 128-bit product service; three handles; CCC writes at 500/700/900 units qualified by a 16-bit connection epoch; ATT events `0x05`, `0x0D`, `0x0E` feed RX | Strong | `R/g2-ble-ota-ring-profiles-recovery.md` |
| Service identity | R1 exposes `BAE80001-4F05-4503-8E65-3AF1F7329D1F` (chars `BAE80010` WwR, `BAE80011` notify, `BAE80012` WwR, `BAE80013` notify) plus Nordic DFU `FE59`; that the G2 client targets `BAE80001` is not pinned in G2 evidence | Inferred | `r1/docs/closures/AUGUST-18-R1-B56EE2-HARDWARE-VALIDATION.md` |
| Ring commands | `ring_service.c` `[0x00472244,0x00472C7C)` dispatches `0x61`, `0x85`, `0x8A`, `0x8B`, `0x8C`, `0x94`, `0x96` (heartbeat, touch report, status/pair frames, PHY, HID validation, battery, wear) | Strong | `R/g2-ring-service-dependency-boundary.md` |
| Phone relay | pb service `0x91` ring events (section 4) | Proven | `R/g2-pb-service-ring-recovery.md` |
| Battery | cache u8 level (<=100) + charging flag; peer sync ID `0x105`; callback list `RING_BAT_INFO` @`0x20073F90` | Strong | `R/g2-service-ring-battery-recovery.md`, `R/g2-cb-ring-battery-recovery.md` |

## 13. Product-test protocol and consoles

| Element | Value | Confidence | Source |
|---|---|---|---|
| BLE request header | `5A A5 7F`, then additive byte checksum; task `ble_production` (prio `0x21`, 4 KiB stack), 3-entry queue, 0x104-B blocks | Strong | `R/g2-thread-ble-production-dependency-boundary.md` |
| Response | prefix `5A A5 FF <x>` (helper `0x0056F42A`), 8-bit additive checksum over the frame appended (`0x0056F46A`); generic 5-B result `{cmd,1,status,1,value}` (`0x00575428`) | Proven | `g2/research/corpus/apollo-main/ghidra/pt-protocol/functions.jsonl` |
| Dispatcher | `0x0056F4A0`, 66 handlers `[0x0056F178,0x00577C3C)`; unsupported -> 5-B response | Proven | `R/g2-pt-protocol-procsr-dependency-boundary.md` |
| Command IDs | `01 05 06 07 08 0B 11 13 17 18 19 1A 1B 1C 20 22 24 25 26 29 2A 2D 2E 30 31 35 38 39 3A 3D 3E 42 43 44 45 46 47 48 49 52 53 54 55 57 58 59 5A 5B 60 61 62 63 64 65 66 67 69 6A 6B 6C 6D 6E 74 75 77 F3`; handler address per ID in `command-map.tsv` | Proven | `g2/research/corpus/apollo-main/ghidra/pt-protocol/command-map.tsv` |
| Case path | case UART frames can carry product-test commands (`[box_uart_mgr]pt cmd execute err`) | Inferred | `R/g2-box-uart-mgr-recovery.md` |
| eAT registry | 21 records `[0x006C9260,0x006C93B0)` {type, name, Thumb handler, 0}: `AT^CLEANBOND`, `AT^BLE_KEEPCONNECT`, `AT^BUZZER`, `AT^AUDIO`, `AT^NUS`, `AT^RM`, `AT^LS`, `AT^MKDIR`, `AT^INFO`, `AT^RESET`, `AT^PSN` (14 B), `AT^IMU_RAWDATA`, `AT^IMU_EULER`, `AT^SCRN_X`, `AT^SCRN_Y` (<193), `AT^ALS_READ`, `AT^ALS`, `AT^BRIGHTNESS`, `AT^ALS_SCALE_READ`, `AT^BRIGHTNESS_READ`, `AT^TP` | Proven | `R/g2-eat-registry-recovery.md`, `R/g2-eat-core-sensor-recovery.md`, `R/g2-eat-bond-connect-recovery.md` |
| eAT core | `at_core.c` `[0x005412E0,0x005415B4)`: `AT_CoreInit`, `AT_Handler`, three-segment parse, exact name match; output provider `0x00541430` | Proven | `R/g2-at-core-recovery.md`, `R/g2-at-nus-recovery.md` |
| `AT^BUZZER` | `note,<0-7>,<0-3>,<1-100>`; `play,<0-10>` (driver table has 9); `start,<1-20000 Hz>,<0-100 %>`; `stop` | Proven | `R/g2-at-buzzer-recovery.md` |
| `AT^AUDIO` | leading `1` acquire / `0` release audio selector 7; reply `AUD_AUDIO+OK` | Proven | `R/g2-at-codec-recovery.md` |
| `AT^RM/LS/MKDIR` | gated on `0x200746A8 == 1`; LS recursive `D <path>` / sizes | Proven | `R/g2-at-fs-recovery.md` |
| `AT^TP` | `1`/`0` diff read/stop, `debug1`/`debug0`, `bsln_read`, `bsln_set`, `gesture_cfg_read`, `gesture_cfg_set,<1-65535 ms>` with readback | Proven | `R/g2-at-tp-recovery.md` |
| `AT^INFO` | product `S200`, HW, SW `2.2.6.10`, codec/touch versions, build `Jul  6 2026 21:37:47`, PSN, BLE name/address | Proven | `R/g2-eat-core-sensor-recovery.md` |
| CLI console | FreeRTOS+CLI 1.0.4-compatible; 76 registrations in 22 groups (system, fs incl. `xip`/`file2xip`/`xip2file`, display, log, imu, codec/audm, pdm, BLE `AT^Ble*`/`AT^EM9305`/`AT^BLEADV`, xmodem, UI apps, set/get, buzzer, gpio, `box_force_out`) | Proven | `R/freertos-cli-console-task-source-candidate-audit.md` |
