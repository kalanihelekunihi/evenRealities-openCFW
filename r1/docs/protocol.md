# R1 BLE protocol (stock 2.2.6.0009)

Tags: **Proven** means byte-pinned in the image or physically observed. **Strong** means several
facts agree. **Inferred** is derived. **Unverified** has no evidence. Sources are repository-root
paths with line numbers. Many sources live in files that are about to be removed (`r1/src`,
`r1/include`, `r1/platform`). Their facts are copied here so the citation remains a historical
pointer.

The stock firmware is nRF5 SDK 17.1.0 + S140 7.2.0. Only the Nordic modules listed in
`toolchain-and-dependencies.md` own GATT, advertising, Peer Manager and DFU. Everything below
that is R1-specific is product code.

## 1. GATT surface

| Item | Value | Tag | Source |
|---|---|---|---|
| Vendor base UUID | `BAE8xxxx-4F05-4503-8E65-3AF1F7329D1F`. Stored in flash at `0x000991A0`, byte-exact match to Bravechip ChipletRing APPSDK | Proven | `r1/docs/PROVENANCE.md:83`; `r1/platform/nrf52840/sdk/openr1_bae8.c:287-290` |
| Service | `BAE80001-…` | Proven (physical, 2.2.8.0002) | `r1/docs/closures/AUGUST-18-R1-B56EE2-HARDWARE-VALIDATION.md:116-124` |
| Channel 1 RX | `BAE80010-…`, write without response | Proven (physical) | same |
| Channel 1 TX | `BAE80011-…`, notify + CCCD | Proven (physical) | same |
| Channel 2 RX (EUS) | `BAE80012-…`, write without response | Proven (physical) | same |
| Channel 2 TX (EUS) | `BAE80013-…`, notify + CCCD | Proven (physical) | same |
| Buttonless DFU | service `FE59`, characteristic `8EC90003-F315-4F60-9FB8-838830DAEA50` (write, indicate, CCCD) | Proven (physical) | same `:124` |
| Buttonless variant | SDK `ble_dfu.c` + `ble_dfu_unbonded.c`, `NRF_DFU_BLE_BUTTONLESS_SUPPORTS_BONDS=0`. SVCI function 3 (`NRF_DFU_SVCI_SET_ADV_NAME`) at `0x00052018` | Proven | `r1/docs/correlation/NORDIC-SDK-CORRELATION.md:388-390,951-955` |
| No other readable characteristics | no flash/UICR/memory read characteristic exists | Proven (physical) | `AUGUST-18-...VALIDATION.md:126-128` |
| BAE8 service implementation | R1 expansion of Nordic `ble_nus.c::on_write` skeleton at `0x0007CF4C`: 4 characteristics, 2 CCCDs | Proven | `NORDIC-SDK-CORRELATION.md:739-744` |
| Queued writes | `nrf_ble_qwr` linked with `NRF_BLE_QWR_MAX_ATTR == 0` | Proven | `NORDIC-SDK-CORRELATION.md:384-387` |
| Sole BAE8 HVX path | `0x000526CC` (2.2.6). In 2.2.7.0005 the HVX Thumb entry is `0x00052969` and the service struct is `0x20006514` | Proven | `r1/docs/PROVENANCE.md:53`; `r1/tools/probes/r1_227_uicr_dump.S:15-16` |

BAE8 service event routing is done by callback `0x0005D5E0`, registered via pointer `0x0005D5E1`
at `0x0004E6E4` into service config `0x000529BC` at offset `0x2C`
(`r1/docs/correlation/BAE8-EVENT-ROUTER-CORRELATION.md:17-34`). Tag: Proven.

| Service event | Route |
|---:|---|
| 2 | BC (channel-1 legacy) receive path (`0x00033AF8`, `0x00033DBC`) |
| 3 | EUS receive reassembler `0x00032198` (channel 2) |
| 6, 7 | link-context group A lookup and glasses-role assignment |
| 8, 9 | link-context group B lookup |
| other | ignored |

## 2. Link parameters

| Parameter | Stock value | Tag | Source |
|---|---|---|---|
| ATT MTU | 247 (central and peripheral) | Proven | `r1/docs/reference/r1-capability-matrix.csv:201` (R1-200); `r1/docs/README.md:776-778` |
| LL data length | 251 | Strong | `r1/docs/README.md:778`; `r1/docs/PROVENANCE.md:117` |
| Links | conn tag 1, count 3, 3 peripheral, 0 central | Proven | `r1-capability-matrix.csv:201` |
| GAP event length | 6 (7.5 ms) | Proven | same |
| HVN TX queue | 4 per link | Proven | same |
| Vendor UUID bases | 2 | Proven | same |
| Attribute table | 2048 B, Service Changed enabled | Proven | same |
| L2CAP CoC | none | Proven | same |
| Security | bonding; no MITM/LESC/OOB/keypress; IO caps none; key size 7..16; enc+id keys both directions; repairing allowed. PM security bytes `31 07 10 03 03` at `0x0004E4B4` | Proven | `r1/docs/PROVENANCE.md:115`; `r1/docs/README.md:761-764` |
| GAP name | `EVEN R1_` + uppercase hex of address bytes 3,2,1. Factory mode appends `_FAC` (nv_r1 byte `0x70 == 0x55`) | Proven (physical `EVEN R1_B56EE2`) | `r1/docs/README.md:801-803,813`; `AUGUST-18-...VALIDATION.md:67-68` |
| DFU-mode name | `B210_DFU_<addr+1>`, e.g. `B210_DFU_B56EE3` | Proven (physical) | `AUGUST-18-...VALIDATION.md:7-10` |
| Appearance | `0x0240` (Generic Keyring) | Strong | `r1/docs/README.md:802` |
| PPCP | min 12 / max 24 (15–30 ms), latency 4, timeout 600 (6 s) | Strong | `r1/docs/README.md:802-803`; `r1/platform/nrf52840/sdk/openr1_advertising.c:87-92` |
| Adv data | flags `0x06`, complete name, appearance; no service UUID, no TX power | Strong | `r1/docs/README.md:804-807` |
| Scan response | manufacturer data, company `0x5245`, 6 address bytes (SoftDevice order) + optional 15-byte product serial (23-byte element observed) | Proven (physical) | `r1/docs/README.md:804-806`; `AUGUST-18-...VALIDATION.md:92-94` |
| Adv modes | normal: fast 100 ms (`0x00A0`) for 60 s (`0x1770` x 10 ms), then slow 1 s (`0x0640`) indefinitely. Factory: fast indefinitely, slow disabled | Strong | `r1/docs/README.md:808-810`; `openr1_advertising.c:16-18,144-149` |
| Single host connection | the retail app allows one phone host at a time. There are two product roles (phone and glasses) | Proven (physical) | `AUGUST-18-...VALIDATION.md:22-24` |

Connection-parameter records sit at flash `0x0009917A` as `{min,max,latency,timeout}`
(`r1/docs/correlation/FRONTIER-204-210-CORRELATION.md:39`; `r1/platform/nrf52840/sdk/openr1_connection_params.c:8-36`). Tag: Proven.

| Set | min | max | latency | timeout |
|---|---:|---:|---:|---:|
| default | 72 | 84 | 4 | 600 |
| fast A | 12 | 24 | 4 | 600 |
| fast B | 12 | 24 | 4 | 600 |
| glasses | 16 | 16 | 2 | 600 |

Policy observer `0x00051AA0` handles GAP connected/disconnected/param-update events. A link is
"fast" iff max interval < 50. On a mismatch it retries: after 4 ms if the actual link is slow,
after 2000 ms if it is fast. Pairs 39/39 and 36/36 set the init marker. The delayed selectors
0/1/2 map to BLE-thread events `0x40/0x10/0x20` (`r1/docs/correlation/CONNECTION-PARAMETER-POLICY-CORRELATION.md:22-50`). Tag: Proven.

## 3. EUS framing (channel 2)

### 3.1 Fragment layer (channel 2 RX/TX)

| Field | Bytes | Value |
|---|---:|---|
| sequence | 1 | descending; 0 terminates. First sequence 0..16 (so at most 17 fragments) |
| CRC-32C of complete logical message | 4 | LE, repeated in every fragment |
| payload | ≤239 | message bytes |

- Maximum BLE value 244. Logical max inbound 4,063 B. Safe outbound 4,062 B. A message whose
  length is an exact multiple of 239 gets an empty terminal fragment
  (`r1/include/openr1/r1_protocol.h:8-21`; `r1/docs/correlation/EUS-RX-REASSEMBLY-CORRELATION.md:21-25`; `r1/docs/README.md:664-665,673`). Tag: Proven.
- Receiver `0x00032198` (424 B, SHA-256 `a91ae73e…88df5`) has one caller at `0x0005D69C`.
  Stock allocates `(first_seq+1)*239` for sequences 2..16 and uses a static buffer for 1. A
  duplicate sequence rewinds and replaces. Stock does not enforce descending continuity or
  repeated-CRC consistency before the final CRC test. On a CRC failure it sends a 6-byte
  transport error (`EUS-RX-REASSEMBLY-CORRELATION.md:17-34`). Tag: Proven.
- Producer: `0x00032408..<0x00032518` (`r1/docs/PROVENANCE.md:13`).

### 3.2 pb_tran fragmenter (diagnostic/export path)

| Field | Bytes |
|---|---:|
| sequence (descending) | 1 |
| CRC-32C (zero init, non-reflected) of logical message | 4 |
| channel | 1 |
| payload | ≤238 |

Logical max 4,096 B, at most 18 fragments. Extent `0x00032598..<0x000326B2`, caller `0x0004E82C`
(`r1/docs/PROVENANCE.md:14`; `r1/include/openr1/r1_protocol.h:16-19`). Tag: Proven.

### 3.3 Model header (12 bytes)

| Off | Size | Field | Notes |
|---:|---:|---|---|
| 0 | 1 | protocol version | must be 100 |
| 1 | 1 | module | 1 system, 2 health, `0x7F` testable. 0 and 3 are null slots, ≥4 rejected |
| 2 | 1 | module version | ingress accepts ≥100 |
| 3 | 2 | serial LE | odd status keeps the caller serial; even status uses the firmware counter (post-increment) |
| 5 | 1 | status | request flag bit 1 is required by health queries; bit 0 is rejected there |
| 6 | 1 | command | |
| 7 | 1 | subcommand | |
| 8 | 2 | total length LE (header + payload) | |
| 10 | 2 | inner checksum LE | see section 4 |

Sources: `r1/src/r1_protocol.c:85-99,160-184`; `r1/docs/correlation/EUS-MODULE-DISPATCH-CORRELATION.md:23-31`;
`r1/docs/correlation/PROTOCOL-RESPONSE-CORRELATION.md:14-26`; `r1/docs/correlation/HEALTH-HISTORY-ROUTING-CORRELATION.md:65-70`. Tag: Proven for layout and gates.

Response status byte: openR1 encoded replies as `0x03 | (code << 2)` and unsolicited
notifications as `0x02` (`r1/src/r1_dispatch.c:355-356,380-381`). The physical trace validated
status bits and serial correlation (`r1-capability-matrix.csv` R1-003), but the complete result-code
table is **Inferred**.

Ingress `0x0008316C..<0x0008321C` (176 B) never checks length or CRC; the reassembly/model layer
does that. The module table is at runtime `0x20006B90`: system dispatcher `0x83CA9`, health
`0x82BE9`, testable `0x84C98` (`EUS-MODULE-DISPATCH-CORRELATION.md:12-31`). Tag: Proven.

Response encoder `0x000828B4..<0x00082A20` (364 B) and constructor `0x00082F9C`: null header →
2, no link → 5, allocation fail → 3, transport fail → 4, success → 0. The allocation is exactly
payload+12 via the FreeRTOS heap (`PROTOCOL-RESPONSE-CORRELATION.md:3-26`). Tag: Proven.

## 4. Checksums

| Name | Algorithm | Stock address | Use | Tag | Source |
|---|---|---|---|---|---|
| CRC-32C (Castagnoli) | poly `0x1EDC6F41`, MSB-first (non-reflected), init 0, xorout 0 | `0x0005D8A4` | EUS/pb_tran outer CRC; diagnostic export file CRC | Proven | `r1/docs/PROVENANCE.md:10`; `r1/src/r1_crc.c:3-18` |
| CRC-16/MODBUS | reflected poly `0xA001`, init `0xFFFF`, table-driven | `0x0005D87C` | ring→phone inner checksum (whole model, bytes 10–11 zeroed); kv.bin records; NV recovery body; sleep.db records; crash record | Proven | `PROVENANCE.md:11`; `r1/src/r1_crc.c:32-43`; `r1/src/r1_protocol.c:58-70` |
| CRC-16/CCITT (compact, phone→ring) | init `0xFFFF`, swap/xor form. The preimage is 9 bytes `[b0,b1,b2,b3,b5,b6,b7,b8,0]` (header bytes 0–3, 5–8, one zero placeholder), followed by the payload | first-party app `BleRing1Model` | phone→ring inner checksum | Strong (11 physical TX models) | `PROVENANCE.md:12`; `r1/src/r1_protocol.c:34-56`; `r1/docs/README.md:660-661` |
| base-131 name hash | `h = h*0x83 + c` over 8 NUL-padded bytes | `0x0005D8CC` | kv.bin class header | Proven | `r1/docs/correlation/KV-STORE-CORRELATION.md:29,45`; `r1/src/r1_kv_store.c:67-73` |
| CRC-32 (IEEE, `0xEDB88320`) | SDK `crc32_compute` | bootloader `0x000FA65C` | DFU image/settings | Proven | `r1/research/bootloader-reconstruction/README.md:95` |

## 5. Command dispatch

### 5.1 System module (1), command 0: 20-entry sorted table at `0x0009A4CC`

Keys are `command<<8 | subcommand` with command = 0 (`EUS-MODULE-DISPATCH-CORRELATION.md:33-35`). Tag: Proven for the key set.

| Key | Name (first-party) | Handler / notes | Tag | Source |
|---|---|---|---|---|
| `0001` | deviceStatus | `0x00083DE4`. 7-byte requested form `[percent,state,01,00,00,00,00]`; state 3 full, 1 charging, 2 not | Proven | `r1/docs/PROVENANCE.md:38`; `r1-capability-matrix.csv:7` |
| `0002` | deviceInfo | `0x00083D5C`. Two 16-byte version slots: app then hardware (`2.2.6.0009`, `603MV1.9.3`) | Proven | `PROVENANCE.md:36`; `r1/docs/README.md:679-680` |
| `0003` | wearStatus | 1-byte state | Strong | `r1/docs/README.md:681` |
| `0004` | userInfo | `0x00084A10`. 12-byte payload (gender/age/UInt16 height…) | Proven | `PROVENANCE.md:39` |
| `0005` | systemTime | `0x000846DC..0x000847BC`. Signed timezone minutes + Unix time in the first 6 payload bytes | Proven | `PROVENANCE.md:43`; `r1/docs/correlation/CLOCK-PRODUCTION-CORRELATION.md:24-25` |
| `0007` | touchSwitch | `0x00084874`. 2 bytes (selector, value): 1 phone (diagnostic), 2 glasses opens/closes touch source 0 | Proven | `PROVENANCE.md:16`; `r1/include/openr1/r1_dispatch.h:37-40` |
| `0008` | pairAuth | `0x000842EC`. Byte `01` selects the phone role and triggers link security. Required before the phone route answers | Proven (physical) | `PROVENANCE.md:40`; `AUGUST-18-...VALIDATION.md:196-220` |
| `0009` | otaStart | enters buttonless DFU (GPREGRET `0xB1`) | Strong | `r1/src/r1_dispatch.c:911`; `r1/tools/probes/r1_227_dfu_proof.S:1-20` |
| `000A` | advStart | `0x00083D04`. Exact 12-byte SET with two 6-byte peer targets | Proven | `PROVENANCE.md:16` |
| `000B` | getAlgoKeyStatus | `0x00083E50`. 25 bytes: status + 24-byte identifier. Clears one-shot latch `0x20006DA5` | Proven | `r1-capability-matrix.csv:196` (R1-195) |
| `000C` | setAlgoKey | 64-byte GoMore key, persisted asynchronously (ACK before write) | Strong | `r1/src/r1_dispatch.c:954`; `r1-capability-matrix.csv` R1-017 |
| `000E` | healthSettings | `0x00083F24`. 12-byte read/write (Unix time + health-enable byte) | Proven | `PROVENANCE.md:91` |
| `000F` | systemSettings | `0x00084524`. 12-byte read; byte 5 = `dev_info` byte 24 bit 1 (REG1 DC/DC). Set ACKs first, then `sd_power_dcdc_mode_set` | Proven | `PROVENANCE.md:18`; `r1-capability-matrix.csv:197` |
| `0010` | deviceSerial | `0x00083DB0`. 15-byte serial or unavailable sentinel | Proven | `PROVENANCE.md:37` |
| `0011` | nvRecover | `0x00084150`. 5-byte envelope + 116-byte identity/calibration body + CRC-16/MODBUS. Fill-only merge of `nv_r1`/`power`/`r_size`; no response on a valid merge | Proven | `PROVENANCE.md:32`; `r1/include/openr1/r1_nv_recovery.h:12-22` |
| `0012` | powerControl | `0x000843C8`. Byte 1 quick restart, 2 ship-mode + shutdown, 3 resume setting. Responds, then raw-100 delay, then effect. Checks only length != 12 | Proven | `r1-capability-matrix.csv:29` (R1-028) |
| `007E` | packet ACK | `0x000842CC` / resolver `0x00083028`. 32-entry first-exact-match consumption; sleep sync marking | Proven | `PROVENANCE.md:42` |
| `007F` | heartbeat family | returns empty success (openR1 behaviour) | Inferred | `r1/src/r1_dispatch.c:907-910` |
| `0082` | removeRingNotify | exact 1-byte SET. Clears `dev_info` byte-24 flag `0x04`, erases peer slots at offsets 8 and 14, restores `CAMH` at offset 20 | Strong | `r1/docs/SECURITY.md:144-153` |
| `0083` | (unnamed) | not recovered | Unverified | – |

System registrations are also pinned as 8-byte records, for example `0B000000513E0800` at `0x9A514`
and `0F00000025450800` (`r1-capability-matrix.csv:196-197`). There are 35 protocol registrations in
total (`r1-capability-matrix.csv:197`).

### 5.2 Health module (2): 14-entry table at `0x0009A454`, dispatcher `0x00082BE8`

Keys are `command<<8|subcommand`. Event-14 record is 8 bytes:
`[metric u8, kind u8 (0 point/refresh, 1 daily), serial u16LE, residue u32LE]`
(`HEALTH-HISTORY-ROUTING-CORRELATION.md:42-70`; `r1/src/r1_health.c:1082-1097`). Tag: Proven.

| Key | Meaning | Metric id |
|---|---|---:|
| `0101` / `0102` / `0103` | HR daily / point / measure (measure requests private event `1002`) | 0 |
| `0201` / `0202` / `0203` | SpO2 daily / point / measure (event `1004`) | 1 |
| `0401` / `0402` / `0403` | HRV daily / point / registered no-op `0x00082DF8` | 5 |
| `0501` / `0502` | activity daily / refresh-only (no direct response) | 4 |
| `0601` / `0602` | sleep daily / sleep detail (private event `100E`) | 6 |
| `7F01` | report-setting selector (optional bool byte) | – |

Temperature (metric 2) and stress (metric 3) are not public history routes. Daily handlers send an
immediate empty response, then asynchronous data. The backfill limit is 259,200 s (3 days)
(`HEALTH-HISTORY-ROUTING-CORRELATION.md:65-77`). Tag: Proven.

### 5.3 Channel 1 legacy frames (BC path)

Router `0x0004E258..<0x0004E428` (464 B) clears the 36-byte workspace `0x2001A174`, copies the
frame, and switches on the opcode at byte 2. Stock does not bound-check the length
(`r1/docs/correlation/LEGACY-COMMAND-DISPATCH-CORRELATION.md:7-35,47-49`). Tag: Proven.

| Op | Handler | Op | Handler | Op | Handler |
|---|---|---|---|---|---|
| `11` | `0x00062584` | `12` | `0x00062546` | `21` | `0x0006244E` |
| `22` | `0x000624F4` | `23` | `0x0006249C` | `24` | `0x000624C8` |
| `34` | `0x00062412` | `37` | `0x000628F6` | `40` | `0x000629D4` |
| `52` | `0x00062834` | `53` | `0x00062388` | `54` | `0x000628AE` |
| `55` | `0x00062A5C` | `56` | `0x00062840` | `57` | `0x000628CC` |
| `85` | `0x00092B98` | `88` | pair-auth response via `0x00033850` (type 2, len 1, byte `2`) | `89` | `0x0006A714` (glasses wear/touch/REG1 route, 7-byte reply) |
| `8A` | `0x00062B4C` | `91` | `0x0006210C` (G2 relay vitals `RingDataPackage`) | `94` | `0x0004E1F8` |
| `95` | `0x00062BEC` | `F2` | `0x00062C30` (factory F2 table) | | |

The opcode `0x89` frame is 7 bytes; byte 3 is a command-valid flag
(`AUGUST-18-...VALIDATION.md:69-76`). The 2.2.7.0005 security audit showed that a 244-byte
channel-1 write overflows the 36-byte workspace (`r1/docs/SECURITY.md:33-35`).

### 5.4 Factory paths

- A factory router `0x000625C0..<0x000627CE` is fed by the factory queue drain `0x00045F84`. It
  handles the same 23 opcodes plus `10` (no-op) and `8B` (status byte at workspace+4, 6-byte reply)
  (`r1/docs/correlation/FACTORY-LEGACY-COMMAND-DISPATCH-CORRELATION.md:5-26`). Tag: Proven.
- Command `F2` high-risk handlers (`r1/docs/correlation/FACTORY-F2-HIGH-RISK-CORRELATION.md:10-20`). Tag: Proven:

| Entry | Action |
|---|---|
| `0x00062D6A` | 4-byte reply, 2000 ms, reset reason 3, NVIC reset |
| `0x00062D84` | PPG profile: byte 4 → 4000, else byte 5 → 2000, else stop; 4-byte reply |
| `0x00062DB0` | reply, 100 ms, `nv_r1` marker `0x5A`, ship mode, 100 ms |
| `0x00062DD4` | reply, 100 ms, ship mode, 100 ms |

- eAT (`AT^…`) command table (37 factory commands in total per `r1-capability-matrix.csv:197`). Tag: Proven:

| Command | Handler | Table record | Behaviour | Source |
|---|---|---|---|---|
| `AT^PMIC_ISNS` | `0x0004F4A4` | `0x000C4250` | current-sense mV | `FACTORY-PMIC-HANDLERS-CORRELATION.md:9-23` |
| `AT^PMIC_OFF` | `0x0004F4D4` | `0x000C4240` | `dev_info` power word = `2 | (mV&0x3FFF)<<2`, power-thread flag 1 | same `:25-33` |
| `AT^PMIC_READ` | `0x0004F524` | `0x000C4210` | YHM reg 9 followed by nine zeros | same `:35-41` |
| `AT^BAT_ADC` | `0x0004EE18` | – | cached mV, percent, battery type | `FACTORY-ACC-BATTERY-DIAGNOSTICS-CORRELATION.md:12,17,37` |

- Factory sensor-stream listener name `"at"`, handles at `0x2000673C+0..16`
  (`r1/docs/PROVENANCE.md:60`).

## 6. Health and sleep synchronisation packets

- **Automatic sync** gate `0x0008B138` (`r1/docs/correlation/AUTOMATIC-HEALTH-SYNC-CORRELATION.md:14-47`). Tag: Proven:
  - It runs only with an authenticated phone link (`0x0004CBB0`).
  - It fires when the timestamp is 0, the clock has gone backwards, or ≥10,800 s have elapsed
    (10,799 does not fire).
  - Leg order: HR `0x0008C150` → SpO2 `0x0008CD60` → HRV `0x0008C750` → activity `0x0008BAEC`
    → unsynced sleep `0x0008B818`.
  - All legs use serial 0. The timestamp is written after the legs regardless of their result.
  - An explicit query (`0x0008B8E8`) resets the timestamp.
- **Sleep packet** builder `0x0008DA24..<0x0008DBFC` (472 B)
  (`r1/docs/correlation/SLEEP-SYNC-PACKET-CORRELATION.md:5-24`). Tag: Proven:
  - 32-byte header. Compact stages carry the type in the low 2 bits and the duration
    (half-minutes) in the high 6 bits.
  - Adjacent equal types merge into 3-byte `[type, u16LE duration]` runs; the run count is at
    header offset 30.
  - Start times < `946080000` force UTC offset 0 and clamp the end to now. Header byte 3 is zeroed.
- **Sleep daily**: `0x00082D14`, iterator `0x0005B39C`. 16-record sync lifecycle, 232-byte body
  bound (`r1/docs/PROVENANCE.md:105`). Sync ACK marks the record with `0x11223344`
  (`PROVENANCE.md:109`).
- **HR / SpO2 / HRV / activity** (`r1/docs/README.md:817-830`; `PROVENANCE.md:84-104`). Tag: Proven:
  - 24 hourly slots per day.
  - HR and SpO2 use u8 avg/max/min, 4-byte narrow items and 16-byte aggregate records.
  - HRV uses u16 values, 7-byte wide items and 20-byte records.
  - Activity uses 144 buckets of 7 bytes and a 144-record offline FIFO of 16-byte records.
  - The HR/SpO2/HRV offline FIFOs each hold 24 records.
  - ACK modes are 0 flash, 1 offline FIFO and 2 RAM.

## 7. Transmit queues and tasks

| Queue | Depth | Source |
|---|---|---|
| BLE type-0/2 TX envelope queue (4-byte pointers). 90 % warning, put timeout raw 100 ticks | 20 | `r1/docs/correlation/BLE-TX-QUEUE-DISPATCH-CORRELATION.md:43-44,58` |
| BAE8 input / EUS shared queue | 50 | same `:77,93` |
| Factory input queue | 8 | same `:106,135` |

The recovered raw RTOS tick constants 100/200/1000 appear in the queue/credit/retry policy
(`r1/docs/PROVENANCE.md:54`). Physical behaviour on 2.2.8.0002 showed 20 queued status requests
answered in order with no loss at 59.7–478.0 ms (`AUGUST-18-...VALIDATION.md:231-236`).

## 8. Buttonless DFU behaviour

- The app callback `0x0005232C` is registered via `ble_dfu_buttonless_init` at `0x000520E4`
  (`r1/docs/correlation/BUTTONLESS-DFU-EVENT-POLICY-CORRELATION.md:17-43`). Tag: Proven:
  - Event 0 (prepare) disables advertising-on-disconnect and disconnects every link.
  - Events 1–3 are diagnostic only.
- Bootloader entry marker is GPREGRET `0xB1` (`BOOTLOADER_DFU_START`). Enter methods: GPREGRET and
  buttonless only (`r1/research/bootloader-reconstruction/firmware-project/config/r1_recovered_config.h:24-27`).
- DFU transport: Nordic Secure DFU object protocol, init packet protobuf (nanopb), ECDSA-P256.
  See `security-and-bootloader.md`.

## 9. openR1 choices (not stock)

- openR1 hardening: strict continuity and repeated-CRC checks in reassembly, rejecting queued
  writes, and the 3–36-byte legacy frame bound. Stock is more permissive.
- openR1 owner authorization (trust-on-first-pairing) and the deny-by-default channel 1
  (`r1/docs/SECURITY.md:42-62,155-161`). Stock gates the phone route only by `pairAuth` role
  selection.
- The response result-code numbering (`R1_RESPONSE_*`, dispatch `RESULT_*`) is openR1's enum and
  was not recovered as named values.
