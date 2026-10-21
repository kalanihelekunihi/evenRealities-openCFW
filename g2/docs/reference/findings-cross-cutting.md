# G2 cross-cutting findings (s200_v2.2.6.10)

> Distilled on 2026-10-21 from the `g2/analysis/` experiment directories and the
> top-level `reviews/` tree, both removed in the consolidation. Only durable facts
> were kept; process narrative, per-run counts, agent coordination and superseded
> ledgers were dropped. Everything remains recoverable from Git tag `pre-consolidation`.

**Citations.** `pc:<path>` means `pre-consolidation:<path>`; read it with
`git show pre-consolidation:<path>`. Unless a path says otherwise it is under
`g2/analysis/`, so `pc:ring-client-2026-09-30/README.md` is
`pre-consolidation:g2/analysis/ring-client-2026-09-30/README.md`.

**Scope and identity.** All facts bind the locked bundle: 4,301,227 bytes, SHA-256
`f4dfb0b4…1b9afa`. The Apollo main OTA payload is 3,523,396 bytes, SHA-256
`36c5b0e4…a27863`. Its headerless flash image (`raw[32:]`) is 3,523,364 bytes,
SHA-256 `19044a72…ba9701`. Main runtime address = file offset + `0x00437FE0`.

**Confidence.** These are static results. Most are backed by Unicorn execution
of the original Thumb instructions with stubbed providers. Nothing here was seen
on a radio link or on hardware unless the entry says so. Scheduler delays are in
**kernel ticks**. They are not milliseconds unless stated.

Related references: [protocols.md](protocols.md), [libraries.md](libraries.md),
[toolchains.md](toolchains.md), [memory-map.md](memory-map.md),
[capabilities.md](capabilities.md).

---

## 1. App-facing protocols

### 1.1 R1 ring GATT client (G2 is central)

Function range `0x004C46C0..0x004C4C66`. Source: `pc:ring-client-2026-09-30/README.md`.
These findings close the UUID gap listed in protocols.md §12, which was "Inferred"
until now.

| Item | Value |
|---|---|
| Discovery call | `0x004C487C` calls `app_discover_service(conn, 16, 0x007880B0, 3, 0x200030D8, handles)`. The last two arguments are on the stack; raw Ghidra drops them. |
| Service UUID | `BAE80001-4F05-4503-8E65-3AF1F7329D1F` at `0x007880B0`, stored LSB-first as `1f9d32f7f13a658e0345054f0100e8ba` |
| Write characteristic | `BAE80010-…` at `0x007880C0` |
| Notify characteristic | `BAE80011-…` at `0x007880D0` |
| CCC | `0x2902` at `0x0078F540`. Discovery records `0x0078DFCC/D4/DC` have trailing flag words `03`, `03`, `06`; the meaning of those flags is unassigned. |
| Default handles | write `0x0010`, notify `0x0012`, CCC `0x0013`. These are stock defaults; don't hardcode them in another client. |
| CCC enable | On open, a 16-bit epoch is incremented. The same callback is scheduled at +500, +700 and +900 ticks, and each run writes `01 00` to the same CCC. The token is `(epoch<<16) \| (final<<8) \| conn`, and the epoch wraps at 65,536. The final attempt emits ring event 4 immediately after `AttcWriteReq` without checking the ATT response, so **event 4 does not confirm notifications**. |
| Close | Clears the connection and handles, increments the epoch, cancels the delayed callbacks and emits ring event 8. |
| RX filter | ATT events `0x05`, `0x0D`, `0x0E` are handled only when `DmConnRole==0`, status is 0 and the handle equals the notify handle. The payload goes to `Thread_SendMsgToRingTaskWithId` (`0x004C548C`). The connection ID is **not** compared. |
| TX | `APP_BleRingSendDataMsg` (`0x004C4B7E`) waits for TX-ready and queues a 12-byte WSF event `0xAC` that holds a **borrowed** payload pointer. It returns 0 for success, disconnect and allocation failure alike. |

### 1.2 Ring command wire format

Code is `ring_service.c`, `0x00472244..0x00472C7C`. Source:
`pc:ring-protocol-2026-09-30/README.md`.

G2 → ring. Each row is the whole byte sequence handed to the BLE send. The
encoders add no length, checksum or framing. The meaning of the `00 1A` and
`00 35` prefixes is unknown.

| Operation | Bytes | Entry |
|---|---|---|
| Glasses heartbeat | `00 1A 94 01` | `0x00472244` |
| Touch-report interval | `00 1A 8A 01 hi lo`. The public wrapper `0x00472362` produces big-endian; the raw encoder `0x004722D8` emits the argument little-endian. The unit is unknown. | `0x00472362` → `0x004C4DE8` → `0x004722D8` |
| Enable / disable ring touch | `00 1A 85 01 00 AA AA AA` / `00 1A 85 01 FF AA AA AA` | `0x00472378` |
| Glasses status flags | `00 1A 89 01 flags 00 00 00`, where `flags = (a0<<7) \| (a1<<6)` | `0x004723D6` |
| Command `0x88` (unknown meaning) | `00 35 88 00` | `0x00472546` |

Ring → G2. `RING_CmdPackageParse` (`0x00472988`) dispatches on **byte 2 only**.
There is no common length, prefix or checksum check. Byte 3 is command-specific.

| Cmd | Behavior |
|---|---|
| `0x61` touch | Byte 3 must be 0 for an event to be emitted. Byte 4 is the type, bytes 5–6 are extra values for types 4/5, and bytes 7–10 are an optional u32 LE timestamp. With a timestamp, any type except 8 is suppressed when the previous timestamp is nonzero and the unsigned delta is below 100. The timestamp is updated before byte 3 is checked. |
| `0x85` | Touch/HID-enable acknowledgement: removes two retry callbacks and publishes "ready" (owner side) or notifies the phone |
| `0x8A` | Report-interval acknowledgement (diagnostic only) |
| `0x8B` battery | Needs ≥ 6 bytes. Byte 4 is the level and byte 5 the charging flag. Forwards the 8-byte record `04 00 02 00 lvl chg …`. |
| `0x8C` wear | Byte 4 is a Boolean. On removal, the elapsed kernel ticks are reported under telemetry key `0x60102`; the log text says "ms" but the value is ticks. |
| `0x94` heartbeat response | Byte 4 `0x20`/`0x40` means a touch/ATI error and schedules disable/enable at +100/+500 ticks |
| `0x96` invalid glasses MAC | Unpairs the currently configured ring. It does not read a MAC from the packet. |

This corrects the positional reading of protocols.md §12: battery is `0x8B`, wear
is `0x8C`, heartbeat is `0x94`. `0x89` is outbound only.

### 1.3 Gestures, input arbitration, and the cross-temple record

Source: `pc:ring-actions-att-2026-09-30/README.md`. Event names come from strings
retained at `0x004C5892`. Display dispatch is at `0x00442D86`.

| Ring type | Input event | Name | Page event / action |
|---|---:|---|---|
| 1 | 0 | SINGLE_CLICK | `0x0A` |
| 2 | 1 | DOUBLE_CLICK | `0x48` |
| 0 | 3 | LONG_PRESS | Page event 8, or system/menu handling (role 1 → system command 3; factory page `0xE0` closes) |
| 5 | 4 | UPROLL | `0x44`; the dashboard scrolls +1 item (+304 px) |
| 4 | 5 | DOWNROLL | `0x45`; the dashboard scrolls −1 item (−304 px) |
| 8 | 14 | RELEASE | `0x4A` with two signed values |

- **Input record.** `0x004C5916(source, event, a, b)` publishes sync ID `0x108` as a
  12-byte record: u16 source, u32 event at +4, bytes a/b at +8/+9. Padding is left
  uninitialized. The ring uses source = 4. Registry `0x006A4620` maps ID `0x108` to
  callback `0x004C5DBC`.
- **Arbitration.** The input manager (`0x004C5DBC`) drops events for device role 2. A
  competing source is suppressed while fewer than 1001 ticks have elapsed. RELEASE
  resets the active source to `0xFFFF`. `DECA_CLICK` (`0x1010`) maps to system command
  `0x109`.
- **Serializer.** `0x00465748` is a 962-byte body that Ghidra failed to decompile. It
  builds the 12-byte body `03 07 src_u16le event_u32le extra_u32le` with
  `extra = (a<<16)|b`. Role 1 sends on route 3; role 2 uses the local route 0 with
  flag 2. A queue failure ends in an assert/fault.

### 1.4 Ring TX ownership, WSF allocator and task configuration

Sources: `pc:ring-actions-att-2026-09-30/README.md`,
`pc:ring-tx-ownership-2026-10-01/README.md`,
`pc:ring-allocator-lifecycle-2026-10-01/README.md`.

- **ATT copy boundary.** `AttcWriteCmd` (`0x00539DEA`) copies the payload into an
  ATT-owned packet (opcode `0x52`, u16 handle) before it returns. The caller's buffer
  can be released after that point. Example: handle `0x10` with payload
  `00 1A 8A 01 12 34` gives `52 10 00 00 1A 8A 01 12 34`. Rejection statuses:
  `0x71` = blocked, `0x77` = MTU too small.
- **WSF ownership.** The dispatcher frees each message with `WsfMsgFree` (`0x0052BA08`)
  after the handler returns, including dropped ring-TX messages. It does not follow
  nested pointers. `WsfMsgSend` has no queue-full failure path because the queue is
  an intrusive list. `WsfMsgAlloc` (`0x004BF99E`) reserves an 8-byte prefix.
- **WSF pools.** `WsfBufInit(0x2940, 0x2004FA98, 4, 0x200003B0)`. The decoded
  configuration (in compressed SRAM init data) gives 16×8, 32×4, 64×10 and 480×20
  blocks, using 10,544 of the 10,560 bytes. Allocation is first-fit by class and
  escalates to larger classes, with no heap fallback. The largest public message
  is 472 bytes. A request of 65,528 wraps to an allocator size of 0.
- **Inline payload budget.** Ceilings for a payload carried inline in the WSF message:
  - 12-byte header: N ≤ 460;
  - 16-byte header: N ≤ 456;
  - ATT's own copy: N ≤ 461;
  - also N + 3 ≤ negotiated MTU.

  A large send needs two free 480-byte blocks at the same time. The unused halfword
  at public offset +10 of the `0xAC` record could carry a TX epoch.
- **Tasks.** The constructors failed to decompile; the values below come from
  executing them.

  | Task | Attribute | Entry | Priority | Stack |
  |---|---|---|---:|---:|
  | ring | `0x0075B8A4` | `0x004C4CED` | 46 | 4,096 |
  | ble_wsf | `0x0075B838` | `0x004D0A4D` | 49 | 16,384 |

  The production command `0x52` sets the current-thread priority to 47.
- **Shutdown.** Task manager `0x004C995E` uses mode bits: 0 poweroff, 1 reboot,
  2 ship, 3 low-power, 4 over-temperature, 5 OTA (OTA runs at most once).
  - The manager posts exit flag `0x800000` and waits up to 5,000 ticks for the
    acknowledgement mask (`0x187A` for OTA, `0x1BFA` otherwise). It continues even if
    the wait times out.
  - The ring task acknowledges as bit 6 *before* it deletes its input queue.
  - No step drains the WSF queue or stops the other TX producers. One such producer,
    `0x005814D4`, calls the ring sender directly.

### 1.5 Microphone stream body (205 bytes)

Source: `pc:audio-stream-2026-10-01/README.md`.

- **Configuration.** The struct at SRAM `0x20108948` holds format 0 (2 bytes/sample),
  frame duration 10,000 µs, 16,000 Hz, 1 channel, channel 0 and 32,000 bit/s. The
  original LC3 helpers turn this into 160 samples and 40 encoded bytes per frame.
- **Body layout.**

  | Offset | Content |
  |---|---|
  | 0–199 | Five LC3 frames (50 ms of mono audio) |
  | 200–201 | metadata0, u16 LE (§1.8) |
  | 202–203 | metadata1, s16 LE (§1.8) |
  | 204 | Wrapping u8 counter `0x2007500E` (pre-increment value) |

- **Path.** `AUD_CodecDmaInt` (`0x0053C6F2`) accepts a DMA buffer up to 40 ticks old
  and rejects it at 41. Accepted buffers go to `SVC_PcmAppProcessData(0, buf, n)`
  (`0x0057ADF8`). This runs the algorithm provider, reads the 1,600-byte front buffer
  `0x005915DC`, calls `SVC_Lc3EncodeMono` (`0x0057A940`) and sends the body through
  `Thread_MsgStreamingNotifyByBle` (`0x00475D78`).
- **Callback slots.** Two 12-byte slots at `0x20073C20` hold {app ID, source,
  callback}.
  - `SVC_PcmAppRegister` (`0x0057AB78`, source 0/1) **replaces** the existing owner.
  - A registered source-0 callback takes over completely and the LC3/BLE stream
    stops. A firmware mod that adds a microphone consumer must forward the data
    itself.
  - `SVC_PcmAppUnregister` (`0x0057ACD0`) clears the slot only when the app ID
    matches. It does not check `source < 2`.
- **Encoder mapping.** Format 0/1/2/3 → 2/4/3/4 bytes per sample; input length must be
  a whole number of frames. The API takes no output-capacity argument.

### 1.6 Audio over ESS: transport

Source: `pc:audio-ble-metadata-2026-10-01/README.md`.

1. `Thread_MsgTxByBle(1, 1, …, body, 205)` (`0x0047564E`) copies the body into a
   heap record of `(len+14)&~3` = 216 bytes: {u32 type = 2, u32 len, data}.
2. The drain `threadBleMsgTxQueueDrain` (`0x0047538C`) takes a TX token (timeout
   argument 50) and calls `APP_BleEssSendDataMsg` (`0x004BE2F6`). Type 2 bypasses the
   multipart encoder, so **there is no `0xAA` envelope, CRC or extra sequence number**.
3. ESS requires a connection, CCC = 1 and no active OTA. It then queues WSF event
   `0xA9` holding a **borrowed** pointer. `essProcMsg` (`0x004BE24E`) calls
   `AttsHandleValueNtf(conn, 0x0864, len, ptr)`.
4. The resulting ATT PDU is `1B 64 08` followed by the 205 bytes, 208 bytes in total.
   The stored ATT MTU must be ≥ 208: 207 is rejected with status `0x77`. The firmware
   never fragments this notification.

Delivery limits:

- The TX CMSIS queue has 150 entries. For transport 1, a new record is dropped (and
  the call still returns 0) once the count reaches 75.
- `ble_msgtx_isConnected` is misnamed. It actually tests for fast connection-parameter
  mode (`0xA3`); when that is false it requests fast mode and still enqueues.
- The OTA gate drops the body *after* encoding, so the counter still advances. A
  sequence gap therefore does not by itself mean radio loss.

### 1.7 ESS GATT table and MTU handling

Source: `pc:ess-gatt-2026-10-01/README.md`. `bleStackRegister` (`0x004B7EC2`)
registers write callback `essWriteCallback` (`0x004BE2B4`) and group `0x20003B38`.
The attribute table is at `0x006DE9D4` and holds 16-byte entries.

| Handle | Attribute |
|---|---|
| `0x0860` | Primary service `00002760-08c2-11e1-9073-0e8ac72e6450` |
| `0x0861` / `0x0862` | Characteristic declaration (property `0x04`) / value `…6e8ac72e6401`: Write Without Response, max 512 |
| `0x0863` / `0x0864` | Characteristic declaration (property `0x10`) / value `…6e8ac72e6402`: Notify, max 512. **The audio stream is sent here.** |
| `0x0865` | CCC `0x2902`, row 3 of the CCC table `0x007518C0` (`65 08 01 00 00 00`) |

- **Handle note.** The "provider handles" `0x0824/44/64/84/A4` in protocols.md §2.1
  match these ATT handle numbers. For ESS, `0x0864` is the notify value handle.
- **MTU-request clamp.** `attsProcMtuReq` (`0x0056C6FC`) raises any peer MTU below 247
  up to 247. It then stores `min(that, configured, HciGetMaxRxAclLen()-4)` and
  replies `03 F7 00`. Peer requests of 23, 207, 208, 247 and 517 all end up stored
  as 247. Clients should negotiate MTU ≥ 208 themselves and must not trust the
  firmware's stored value as proof that the peer agreed. The grammar for writes to
  `0x0862` is not decoded.

### 1.8 Stream metadata semantics

Sources: `pc:audio-ble-metadata-2026-10-01/README.md`, `pc:audio-angle-2026-10-01/README.md`.

**metadata0** is a dimensionless energy ratio from `SVC_SSRProcess` (`0x0059173A`).
It is not in dB.

- Inputs: `algo_front_data_preprocess` (`0x005915EA`) splits 800 stereo pairs into
  per-channel mean squares and a mono mix `L/2 + R/2`. A 10-entry u64 ring
  (`0x00591C26`) supplies the baseline.
- Formula: `cur = (msL+msR)/2`, `base = sum(window)/10`,
  `m0 = low16((cur+1)/(base+1))`. The result is 0 if either channel energy is 0.
  There is no clamp, so it wraps at 65,536.

**metadata1** is a signed integer angle in degrees from `service_algo_source_angle`
(`0x00591BA4`).

- Call chain: cross-correlation `0x005918CC` → delay `0x005918B0` → clamp
  `0x0059188E` → `asin` `0x0043C260`.
- Parameters: 800 samples, lags −10…+10, fs = 16000.0, spacing = 0.14, c = 343.0,
  thresholds 0/0.
- Correlation: positive lag k computes `Σ L[i]·R[i+k]` in int64. The earliest lag
  wins ties.
- Angle: `asin(clamp(lag/16000·343/0.14, −1, 1))·180/π`, truncated toward zero and
  narrowed with `SXTH`.

| Lag | −10 | −3 | −1 | 0 | +1 | +3 | +10 |
|---|---:|---:|---:|---:|---:|---:|---:|
| Degrees | −90 | −27 | −8 | 0 | 8 | 27 | 90 |

The angle saturates for |lag| ≥ 7. **Silence returns −90**: all lags tie, so −10
wins. The stream carries no validity or confidence flag, and physical left/right
orientation is unknown.

**Client guidance.** Parse the 205-byte notification value directly; there is no
length prefix. Decode it as 5 × 40-byte LC3 frames (16 kHz mono, 10 ms, 32 kb/s),
then metadata0 at 200, metadata1 at 202 and the sequence byte at 204. Reusable
host headers existed in the batch dirs: `ring_client.h`, `ring_protocol.h`,
`ring_actions.h`, `ring_tx_budget.h`, `audio_stream.h`, `ess_audio.h`,
`ess_gatt.h` and `angle_model.h`.

## 2. Other firmware facts recovered in these batches

| Fact | Detail | Source |
|---|---|---|
| EM9305 host transport | The firmware selects **IOM6**. `0x004B48C8` passes module 6, and the base is derived as `0x40050000 + 6<<12 = 0x40056000`. Other bindings: ready = GPIO117 (read through `0x40010410` bit 21, a GPIO read register, not a BLEIF status register); chip select GPIO149; reset GPIO93; configuration clock GPIO15 (40 pulses); IRQ59 at priority 4. The GPIO writer `0x00480FD6` clears through `0x40010458` and sets through `0x4001043C`. This settles the open question in `docs/hardware/components/em9305.md`. | `pc:source-discovery-parallel-2026-10-09/TRANSPORT-CROSS-VERSION-COMPARISON.md`, `pc:fresh-scan-final-reviewed-successor-2026-10-09/SUMMARY.md` |
| Apollo main reset | The reset vector is `0x005E4233` (Thumb entry `0x005E4232`). `0x005E4294` is the downstream IAR runtime entry, not the reset handler; memory-map.md conflates them. The reset chain: (1) MSPLIM/PSPLIM = `0x2007D000`; (2) stack seal `0xFEF5EDA5` via `0x005E4254`; (3) CP10/11 enable with FPSCR = `0x02040000` (`0x005E4270`); (4) VTOR = `0x00438000` (`0x005E4228`); (5) relative initializer table at `0x005E42B4`. | `pc:shortcut-package-discrimination-20261009-agent2/REPORT.md` |
| IAR scatter table | `0x0075D3C8..0x0075D410` holds 5 destination records, all absolute (no r9/RWPI flag). Three compressed inputs end exactly at the image EOF. Zero-init handler `0x005FA01E` clears `[0x20004558,0x20075048)`. | `pc:shortcut-three-lane-continuation-20261010/REPORT.md`, `pc:shortcut-arm-tools-20261009-agent3/fff2-tail/REPORT.md` |
| TLSF (main) | `mapping_insert` `0x004CFF6C`, `mapping_search` `0x004CFF9A`, `search_suitable_block` `0x004CFFC2`, `control_construct` `0x004D0524`, `block_locate_free` `0x004D0484`, `adjust_request_size` `0x004CFF42`. Configuration: SL_INDEX_COUNT_LOG2 = 5, ALIGN_SIZE_LOG2 = 2, FL_INDEX_SHIFT = 7, 24 first-level lists, minimum block 12 (`0x0078F4C4`), maximum `0x40000000` (`0x0078F4C8`). The control block is 3,188 bytes: sentinel +0, FL bitmap +16, 24 SL bitmaps +20, 24×32 heads +116. The assert path string is `third_party\tlsf\tlsf.c` line 568, and the assert provider is `0x004D09B4`. | `pc:shortcut-arm-tools-20261009-agent3/{REPORT.md,search-successor/REPORT.md}`, `pc:shortcut-tool-automation-20261009-agent2/REPORT.md` |
| TDK ICM-45608 | SRAM write path: `0x00508E92` → `0x00508FA6` (register `0x7C` for the address, then `0x7E` for each data byte, with a delay of 4 per step). GAF setup `0x00506ECA` writes a 125-byte patch from `0x006D53D8` to SRAM `0xC80`, then writes the key from patch+8 to `0xB4`. The patch (SHA `80eb396b…`) **exactly equals official 1.0.7 and 1.1.2**; 1.1.3 and 1.1.8 use a different 189-byte patch. The mounting write `0x00507710` sends 18 bytes from the Q14 cache at `0x20000E00` to SRAM `0x1AC`. | `pc:coverage-audit-parallel-2026-10-09/TDK-TRANSPORT-CALLGRAPH-REPORT.md` |
| BQ27427 | Descriptor table at RAM `0x200006EC` (decoded init data). Entry 6 = subclass 105 / block 0 / byte 5. Stock writes the constant `0x28` and recomputes the checksum (`0xEC` in the fixture). Zephyr's driver instead clears bit 7 selectively; the two approaches differ. | `pc:source-backed-actionable-findings-reviewed-successor-2026-10-09/SUMMARY.md` |
| MX25U25643G NOR | B7 mode check reads RDCR (`0x15`) and tests bit 5 (`0x20`, which agrees with the vendor 4-byte flag). QE is set via RDSR/WRSR bit 6 with readback. `6C` read checks only the start address (< `0x02000000`), not address + length. 8 turnaround cycles. | `pc:source-discovery-parallel-2026-10-09/FLASH-VERSION-BOUND-COMPARISON.md` |
| HCI LE Read Supported States | Reset consumer `0x00569B56` copies 8 bytes from event offset 6 to `0x200714D8`. It skips the status byte and has no length guard. | `pc:fresh-provider-evidence-audit-20261009T192906Z/REPORT.md` |
| Fonts and images in main | 11 custom LVGL `fmt_txt` 4-bpp bitmap fonts with descriptors at `0x0077F374, 0x0077F414, 0x0077F428, 0x0077F450, 0x0077F464, 0x0077F478, 0x0077F48C, 0x0077F4B4, 0x0077F504, 0x0077F518, 0x0078001C`. Mapped codepoint counts: 102/401/299/13/399/314/100/13/16/11/157. Callbacks: descriptor `0x004B26A4`, bitmap `0x004B239C`, cmap `0x004B2774`; opacity table at `0x00786950`. The byte-aligned row stride is `floor(w/2)+1`, not ceil. 428 valid LVGL9 L8 image descriptors (28-byte schema) lie within `0x007682B0..0x00774A84`. No PNG/sfnt/gzip container is present. | `pc:coverage-audit-parallel-2026-10-09/bundle-accounting-2026-10-13/{REPORT.md,resource-expansion/REPORT.md}` |
| Other tables | 512-byte TinyFrame CRC16/ARC table; three DSP bit-reversal/Q15 tables (2,272 bytes); LittleFS geometry (read 16 / prog 256 / block 4096 / count 3008 / cycles 500 / cache 4096 / lookahead 256), identical in main and bootloader | same |
| GX8002 codec startup | Stage 1: `runtime = child + 0x0FFFFFE8`. Wrapper `0x10000ACC` follows the SDK `spl_board_init_r` order; NOR-only boot (mode 2); UART at 115200. Stage 2 (`runtime = child + 0x10023400`): reset `0x10023500` (PSR = `0x80000200`, SP = `0x2002F7FC`); BSS `[0x20026D80,0x2002ECEC)`; `system_init` `0x1002354C` (MPU region 0 = 4 GB, CCR \|= 3, VBR = `0x10023400`, VIC init) → `main` `0x10026314`. | `pc:shortcut-csky-authenticated-20261009-agent1/REPORT.md` |
| GX8002 IRQ and PMU | `gx_request_irq` `0x1002553C` stores {callback, argument} in 8-byte rows at `0x20026EF4`. `gx_irq_handler` `0x10025574` passes (index−32, argument). PMU request 13 = GPIO \| audio \| I2C (masks GPIO 1, RTC 2, audio 4, I2C 8). The audio init callbacks are record `0x10026214`, config `0x10207234` and update `0x10207020`; the energy-VAD and FFT-VAD slots are null. The PLL retry offsets table is `{0,10,15,−10,−15}`. | `pc:shortcut-provider-archive-20261009-agent1/REPORT.md`, `pc:shortcut-provider-closure-20261009-agent1/REPORT.md`, `pc:source-discovery-parallel-2026-10-09/FINAL-CONSTRAINTS.md` |
| UART3 | UART3 carries GX8002 control/DFU, not temple sync. The codec RX ring keeps the newest 63 bytes. Logger sink: UART channel 1 (installer `0x0054171C`). Channel 3 has a 1,024-byte TX queue; the default logger has none. | `pc:rescan-2026-10-09T032723Z/REPORT.md`, `pc:rescan-2026-10-09T023256Z/REPORT.md` |
| `am_hal_delay_us` | `[0x004807A0,0x004807F0)` uses floating-point scaling with an HP adjustment of 24, which matches pinned SDK 5.1. SDK 5.2 computes `us*83+(us+1)/3` with an adjustment of 25, so 5.2 is excluded for this function. | `pc:coverage-audit-parallel-2026-10-09/delay-sdk52-discriminator/REPORT.md` |

## 3. Upstream source identification and external-source hunts

All 2,557 registered binaries and 34,282 source files under `third-party/` were
scanned. This covered 570,457 sized ARM, ARC, ARCv2 and C-SKY functions. The scan
produced:

- 545 exact occurrences;
- 168 unique exact provider functions, each confirmed by native `ar`/`readelf`
  extraction;
- 462 C-SKY relocation-masked candidates that are not accepted;
- 247 lexical source anchors, mostly Cordio and LVGL.

The scan used anchors of ≥ 24 bytes with ≥ 5 distinct byte values.

The third-party frontier is **exhausted for the registered corpus**. Further
progress needs new authentic inputs (§7). Sources:
`pc:shortcut-cross-corpus-20261009-agent3/REPORT.md`,
`pc:shortcut-theory-fourth-frontier-20261009/REPORT.md`.

### 3.1 Found or confirmed

| Upstream / input (pin) | Result |
|---|---|
| **IAR EWARM 10.10.2 DLIB** (`dl7Mx_tlns.a`, `rt7Sx_tlg.a`) | Ten stock bodies match these archives byte for byte: `isxdigit` `0x00595984`, `strcat` `0x00567C80`, `strcspn` `0x00541B30`, `__iar_Strrchr` `0x00567C64`, `strspn` `0x00541B52`, `_PutcharsDefault` `0x00482684`, `_GetN` `0x004D15FA`, `_UngetN` `0x004D161C`, `ranmatch` `0x004D2112`, `__iar_zero_init3` `0x005FA01E`. The same bytes appear in 11–17 archive variants (6 for zero_init3), so **they identify neither the release nor the RWPI choice nor Normal/Full DLIB**. Structure offsets: `_GetN` uses fields +12/+16; `_PutcharsDefault` uses +8/+44. `pc:shortcut-iar-shortlist-review-20261010-daybreak/REPORT.md` |
| **TLSF v3.1** | Behavioral and assert-string match; see §2 |
| **Ambiq Zephyr** `2e347415` (`third-party/reference/ambiq-zephyr`) | EM9305 `0xFFF2` is the 8-byte local-supported-feature mask; already folded into protocols.md §10. `pc:shortcut-source-gap-20261009-agent1/REPORT.md` |
| **AmbiqSuite 5.2.0** ZIP (SHA `d9751350…`) | The unchanged `am_util_stdio` formatter links under GNU ld 2.47. The SDK startup/ICF files are not the original project. `pc:coverage-audit-parallel-2026-10-09/sdk-runtime-link-review-2026-10-10/REPORT.md` |
| **EM9305 v4.2 standard image + SYM**, personal mirror `C0R3YY2/em9305_original` @ `e4412bc9` | 40 exact named-symbol matches, each unique in the 211,948-byte payload. 18 of them **distinguish v4.2 from v4.6**: 7 have the same size but different bytes, and 11 differ in size. 4 are data-shaped. `RF_RfChannel2BleChannel` = `llConvertRfChanToChanIdx`. The mirror is unlicensed (128 MB); only 4 files were kept, in the ignored `third-party/local-vendor/sources/em9305-v4.2-public-mirror/`. Its build scripts show `ccac`/`arac` and ARCv2 EM core4 / `em9305` profiles. `pc:shortcut-three-lane-continuation-20261010/REPORT.md` |
| **EM9305 SDK v4.6** (local, authorized) | QPC `SWI1` and `QEQueue_init` match exactly; 8 QPC routines changed. Timer0/1 bodies (194 B each, `0x00305B1C`/`0x00305BE0`) differ. v4.6 rewrote IRQ priority tables (PR12531), so they must not be carried back to 4.2. The release notes give v4.2 discriminators: controller Mango 2.2.0 (PR9194/9337), CTE design 244581; v4.3 adds `RF_HandleInterrupt_Tx`; v4.4 adds `IRQ_AreInterruptsEnabled`. `pc:source-discovery-parallel-2026-10-09/EM9305-OFFICIAL-VERSION-BOUNDARY.md` |
| **QP/C 6.5.1** `416dcec8` | `QEQueue_init` `[0x00310F5C,0x00310F74)`, `QK_sched_` `0x00311634` (56 B), `QK_activate_` `0x00311554` (144 B; active-object table `0x0080131C`). **There is no ARC port.** The QPC software LOG2 fallback cannot stand in for the hardware extension (§5). |
| **Infineon PDL `mtb-pdl-cat2` release-v2.21.0** `35f17146` | 54 of 54 selected functions match (4,952 bytes). `Cy_SCB_ReadArray` at `0x9250` (30 B) is a behavioral match but has not been compiled. With GNU 14.2.1, unchanged source reproduces Configure (424 B), Capture (48 B) and ConfigureScan (160 B) **exactly**; this resolves the old 24-byte Configure mismatch. Configure is identical in every release from 2.3-Beta2 to 2.21. |
| **Arm GNU 14.2.rel1** runtime (metadata `ae6adf75`: gcc `a05ea1e5`, newlib `7923059b`, binutils `74c7803f`) | Touch runtime rebuilt from source: `__udivsi3` + zero hook (280 B), `__divsi3` `[0xA7D4,0xA9A0)` (460 B) + `__aeabi_idivmod` (8 B), memcpy (18 B), nano memset `[0xA9D4,0xA9E4)` (16 B), and CRT (152 B). The source-produced runtime totals 1,074 B. Archive SHA `62a63b98…`. `pc:coverage-audit-parallel-2026-10-09/{SIGNED-MEMSET-REVIEW.md,COMPILER14-REVIEW.md}`, `pc:source-discovery-parallel-2026-10-09/COMPILER-RUNTIME-FOLLOWUP.md` |
| **NationalChip `lvp_kws`** `8bf9ee5c` `lib/libdriver_release_v1.0.6.a` | All 41 members and 585 functions were compared. Exact or relocation-only providers include `_ain_reset` `0x10203C88` (320 B), `gx_audio_in_*` setters, `gx_audio_in_init` `0x102047E4`, `reg_get/set/clr_bit` `0x102055C0/CC/DC`, `npu_en_interrupt` `0x1020566C`, `gx_pmu_ctrl_set/get/enable` `0x10025D74/0x10024810/0x100248CC`, `gx_clock_set_module_enable` `0x10025080`, `gx_request_irq`, `gx_irq_handler`, `gx_get_time_us` `0x1002585C`, `gx_mdelay` `0x1002598C`, `gx_snpu_init` `0x10205CF4` (literal-pool layout only), `snpu_isr` `0x10205CE0`, `_AudioInISR` `0x10025E48`, `gx_audio_in_set_interrupt_enable` `0x102047B8`, `gx_audio_in_exit` `0x10204984`, `gx_snpu_exit` `0x10205D40`. Lifecycle C matches `LvpKwsInit` `0x10206D90`, `LvpAudioInDone` `0x102073F8`, `LvpPmuInit` `0x10207680`, `LvpInitMaxKws` `0x10208944`. The app helpers `0x1020975C`/`0x10209770` are first-party. `printf_` matches tinyprintf's 3-argument wrapper; stock `memset` realigns the pointer, so it is not `utility/libc/memset.c`. The VAD diagnostics at `0x1020744A/7510/752E` are active in KWS `lvp_audio_in.c:668/699/730` but commented out in AIoT. |
| **NationalChip C-SKY DSP** (inside `lvp_kws` `utility/libdsp`) | 9 exact relocation-free sections (1,606 B) in BINH-B stage 2, package offsets `0x47914..0x48189`: `csky_split_rfft_q15`, `csky_split_rifft_q15`, `csky_shift_q15`, `csky_abs_max_q15`, `csky_copy_q15`, `csky_fill_q15`, `csky_radix4_butterfly{,_inverse}_q15` (530 B each), `csky_bitreversal_16`. The cross-corpus scan adds `csky_cos_f32`/`csky_sin_f32` and the VUI `LvpCTCModelInitSnpuTask`. |
| **Pigweed HCI Emboss** `e175383a` | Protocol-layout reference. Stock `HciLeReadSupStatesCmd` `0x0052B37C` and its consumer agree with the schema. |
| **TDK ICM-45608** Arduino 1.1.8 `edaf3359` vs registered 1.1.2 `b79ae575` | Stock patch = 1.0.7/1.1.2 lineage; see §2. The unequal-ODR key write to `0x50` (added in 1.1.8) is absent. |
| **Zephyr BQ274xx** `87a40fa6`; **Linux OPT3001** v6.6 `ffc25326` (GPL-2.0); **Macronix MX25U25643G LLD 1.1b** (proprietary, internal-use only) | Protocol references only. None is a stock source. |
| **Infineon MSCLP demo** `2944e626` (`third-party/reference/infineon-msclp-demo`) | Only maps vocabulary to CapSense Configurator 6.20 concepts. Excluded as the target configuration: stock `CE_CTL = 0x80000100` leaves LP raw IIR disabled, while the demo enables it. |
| FreeType `86bc8a95` (2.9.1 header), Ambiq LVGL `5be8e0ae` (9.3.0), LVGL core `344c7c31` | Pins used for glyph-loader and font joins. `FT_GlyphLoader_Reset` `[0x00524BC4,0x00524C1E)` and `Rewind` `[0x00524BA8,0x00524BC4)` follow `ftgloadr.c:105–123`. |
| Analysis tools: Ghidra-MCP `9cc29c0f`, Ablation `97e051b4`, REA `7aa4d768`, embARC OSP `67ea926c`, lvp_aiot `d4aa0094` | Registered as references (`third-party/tools/*`, `third-party/reference/*`). embARC and AIoT are comparators only. `lvp_aiot` vs `lvp_kws`: 318 files identical, 68 differ, 38 new. |

### 3.2 Ruled out or unavailable

| Candidate | Why it is excluded |
|---|---|
| Ambiq **Apollo_DFP 1.5.2** pack (SHA `1b63ff8f…`) | Its `startup_apollo510.c` is entirely `#if 0`. Its `Reset_Handler` powers SSRAM and its `SystemInit` writes CCR cache bits and `SystemCoreClock`; stock does neither. Its system file declares 496 vectors while the startup declares 256. |
| Ambiq SDK 5.2 | Excluded for `am_hal_delay_us` (§2). The alpha2 → alpha3 change to `am_util_ble_em9305.c` is only a revision comment. |
| Infineon **CAT2 DFP** | Its startup is a dummy that emits a compiler error. The target needs the generated CapSense `.cycapsense` + generator version, which were never obtained. |
| **STM32CubeG0 v1.6.3** NUCLEO-G0B1RE FreeRTOS_Timers MDK project | Uses ArmCC 5.06u6 with the RVDS CM0 port; stock uses Arm Compiler 6 with the GCC CM0 port. Also, DFP 2.0.0 (2025-03-20) removed Cube HAL from packs (DFP 1.4.0 → HAL 1.4.2, 1.5.0 → HAL 1.4.5). |
| **Goodix GR551x** `app_error.c` (2.0.2/2.1.x, 46 rows) | Stock matches the historical 1.7.0 43-row fingerprint, which is not available in the public history. This does not mean G2 contains a GR551x. |
| `lvp_aiot` as producer | The PLL table has 3 entries (vs 5 in stock) and its VAD diagnostics are commented out. |
| NationalChip `npu_dis_interrupt` at `0x1020566C` | A masked-relocation false positive: all 7 stock calls go to `reg_set_bit`. This case illustrates why relocation masking alone is not enough. |
| GX8002 I2S `gx_i2s_set_five_wire_mode` (830 B section) | No raw match. The I2S source is absent; only the `.o` exists. |
| Private / unavailable | **IAR** DLIB sources (shipped only in the exact producer product package under `arm/src/lib`). **NationalChip `lvp_tws`** (private GitLab `git@gitlab.com:nationalchip/lvp_tws.git`; the SSH key was denied; the public release arrays are empty). **EM9305 v4.2 SDK** (registration-gated at `forums.emdeveloper.com`). **MetaWare T-2022.09**. **NemaGFX implementation**. **Packetcraft LL**. **Ambiq private 5.1.0 HAL**. **Resident ROM / factory bytes**. |

## 4. Whole-bundle byte accounting

This section gives the final method and final numbers. Earlier assessments,
rescans and dashboards are superseded.

**Method rules.** Keep these stages separate:

- classification;
- raw export;
- reviewed pseudocode;
- exact match;
- source-produced bytes;
- integrated replacement.

Never sum stages or derive a code denominator by subtraction. Use half-open
intervals per image and never merge decoded, RAM or alias images by address. All
payload slices include the 32-byte OTA/EVEN headers where applicable. Touch decoded
offsets need +`0x20` (FWPK) to become payload offsets. Sources:
`pc:coverage-audit-parallel-2026-10-09/{COMPONENT-COVERAGE-MATRIX.md,address-coverage-sample-2026-10-11/REPORT.md,component-percentages-2026-10-10/REPORT.md}`.

**Exclusive partition** (2026-10-13). All 4,301,227 bytes are accounted with no
holes or overlaps. The six payloads total 4,300,283 bytes. The remaining 944
transport bytes are the 176-byte outer header/TOC/trailer plus six 128-byte
component headers. All six CRC32C checks pass. Source:
`pc:coverage-audit-parallel-2026-10-09/bundle-accounting-2026-10-13/REPORT.md`.

| Component | Payload | Confirmed code | Confirmed data | Suspected | Unknown |
|---|---:|---:|---:|---:|---:|
| codec | 326,092 | 0 | 123,120 | 110,188 | 92,784 |
| ble_em9305 | 211,948 | 0 | 1,069 | 209,395 | 1,484 |
| touch | 34,464 | 0 | 1,188 | 28,484 | 4,792 |
| case | 55,784 | 4,572 | 6,610 | 39,720 | 4,882 |
| apollo_bootloader | 148,599 | 0 | 1,897 | 127,231 | 19,471 |
| apollo_main | 3,523,396 | 88 | 468,631 | 2,228,805 | 825,872 |
| **Bundle** | | **4,660** | **603,459** | **2,743,823** | **949,285** |

Notes on the partition:

- "Confirmed code" is deliberately narrow. "Suspected" covers function envelopes and
  string candidates.
- The 9,164-byte GXNPU command stream is suspected accelerator code.
- 177 resource-vs-envelope conflicts are retained.
- An orthogonal font overlay adds 65 spans totalling 204,732 B; 204,695 of those
  bytes were previously unknown.
- `resources/g2/s200-v2.2.6.10/manifest.json` catalogues 1,191 byte-exact resource
  records (785,326 bundle bytes).

**Artifact-representation fractions.** These measure which bytes are represented
in exported artifacts. They are not completion figures.

| Component | Raw pseudocode cohort (functions) | Raw-export byte union | Validated listing bytes |
|---|---|---:|---:|
| Apollo main | 8,475 / 8,853 (378 failures) | 1,555,524 (44.15%) | — |
| Bootloader | 849 / 903 | 112,506 (75.71%) | — |
| Touch | 308 / 308 | 27,879 (80.89%) | — |
| Case | 435 / 435 | 43,072 (77.21%) | — |
| Codec | 929 / 929 (five export images) | 92,560 (28.38%) | 36,484 (11.19%) |
| EM9305 | unknown | unknown | 210,072 (99.11%); 1,876 bytes unrepresented |

Other points:

- **Packaging.** The reference package is still 100% `official_blob`
  (4,300,283 / 4,300,283).
- **Builds.** No payload has a complete source build (0 of 6 components), and no
  byte-identical bundle exists.
- **EM archive match.** The EM9305 relocation-normalized archive match covers
  157,122 / 210,888 bytes (74.50%, 1,494 functions). That is archive matching, not
  source recovery.
- **Canonical images.** There are 33. Size anchors:
  - main decoded images: `0x20000000` = 17,752 B, `0x20080000` = 769,646 B;
  - 12 decoded or initialized images totalling 795,378 B;
  - EM9305 records 0/1/2/3 = 224/656/56/210,888 B;
  - codec sub-images as listed in memory-map.md.
- **External NOR.** The MX25U25643G is 32 MiB: LittleFS `[0x01400000,0x01FC0000)`,
  FlashDB sysenv `[0x01FC0000,0x01FF8000)`, factory `[0x01FF8000,0x02000000)`. It is
  **not in the OTA**, and no dump exists.

## 5. Compiler and toolchain conclusions

These refine [toolchains.md](toolchains.md); where they disagree, this section is
newer.

| Payload | Conclusion |
|---|---|
| Apollo main | IAR EWARM is confirmed. The **10.10.2 archives are byte-compatible** with 10 DLIB/runtime leaves, but those leaves do not choose a release or variant. The scatter table has 5 absolute (non-RWPI) records. `__iar_zero_init3` treats a destination with bit 0 set as r9-relative and needs lengths ≥ 4. To narrow the release, obtain the `.ewp`/ICF/map, or an IAR release whose leaf bodies differ. The SDK link probe (Apple clang 21, Cortex-M55 hard-float) shows that soft-float/hard-float mixes are rejected at link time. |
| Touch | **Arm GNU 14.2.1 `-Og`** reproduces three PDL sections exactly. Earlier evidence allowed GCC 10.3–13.3; that range is a compatibility interval, not a unique producer. The runtime is nano newlib + libgcc built from 14.2.rel1 sources. |
| Case | Arm Compiler 6 + armlink (reconfirmed). The official ArmCC 5 example project is excluded. A Clang candidate for the 28-byte ST FLASH bodies differs (27/25 B). The historical ordinary/option FLASH **unlock labels are reversed**. Tested UART receive helpers match HAL v1.4.5. |
| GX8002 codec | The SDK DSP objects' DWARF records `GNU C11 6.3.0 -mcpu=ck804ef -mfloat-abi=hard -g -O2 -fno-builtin -fstrict-volatile-bitfields -ffunction-sections -fdata-sections`. The SDK Makefile requires C-SKY ToolsV3.10.15 Minilibc abiv2 B20190929 / GCC 6.3.0; its `ck803` lib directory label is not a CPU claim. Toolchain facts: the CK804 ISA includes BNEZAD and MULA.32.L (binutils `32f97f34`); vendor GCC (`1e9b7044`) sets `STACK_BOUNDARY` to **4 bytes**, contradicting the published ABI's 8. GCC 6.3 compiles 5 of the C units, but 3 selected sections differ. Seven assembly sources reproduce 9 sections (1,606 B). |
| EM9305 | Built with MetaWare `ccac`/`arac` (ARCv2 EM). The stock word `0x3D2F1000` at `0x0031163E` is the vendor APEX extension **`log2p1 r13,r0`** (opcode 7/0, `LOG2_Extension.1_0`, `UniPHY_ARC_ExtensionLibrary v1.0.0`). Its arithmetic semantics (zero, sign, flags) are unspecified, and standard binutils prints it as `.word`. |

**Analysis-tool defects found.** Sources: `pc:shortcut-ghidra-mcp-20261009-agent2/report.md`,
`pc:shortcut-csky-authenticated-20261009-agent1/REPORT.md`,
`pc:shortcut-ablation-rea-20261009-agent3/REPORT.md`,
`pc:shortcut-tool-exhaustion-20261010-daybreak/REPORT.md`.

- **Ghidra C-SKY `movih` (`32b_data.sinc`).** The instruction shifts a 2-byte
  temporary left by 16, so it lifts to 0. Fix: zero-extend before the shift
  (`csky-movih-width.patch`).
- **Ghidra C-SKY `mfcr` (`32b_priv.sinc`).** The instruction writes to
  `i32_c_rz` instead of `i32_r_rz`, so the destination register is never written.
  Fix: `mfcr-destination.patch`.
- **Patch scope.** Both fixes were applied only in a private copy of the
  processor. Until they are reviewed and installed, Ghidra constant propagation and
  emulation are unreliable on affected C-SKY code.
- **Ghidra C-SKY `INS` operands.** These print as size−1 and offset, while GNU prints
  end-bit and start-bit. This is a display difference, not a semantics bug.
- **Ablation.**
  - It labels ARC and C-SKY as x86_64, and its fallback ARC decoder ignores LIMM.
  - Direct-call inventory is complete for spans ≤ 4 KiB but missed 1,198 calls in 23
    larger spans.
  - Its "strings" output is often just instruction bytes.
- **REA.** Admits only x86, x86-64, ARM and ARM64 ELF, so ARC and C-SKY are rejected.
  On a single-body ELF its call graph comes back empty.
- **Ghidra-MCP.** `open_project` can report success while the bridge is still attached
  to another project.
- **Ghidra decompiler.** It drops floating-point (`d0`–`d4`) and stack arguments. It
  also misreported the ring-protocol queue drain `0x0047538C`, wrongly showing its
  branches as unreachable.
- **Unicorn.** The M-class model rejects double-precision VFP, so use Thumb without
  MCLASS. Valid-memory-write hooks corrupt the IT state. pyelftools rejects C-SKY
  relocation type 1; use the target `readelf` instead.

## 6. Known stock-firmware bugs and hazards

Each item is local-semantics evidence with synthetic scheduling. None was observed
on hardware.

| # | Hazard | Where | Source |
|---|---|---|---|
| 1 | Ring TX passes a **borrowed stack pointer** across the WSF queue. With a delayed consumer, an earlier send transmits a later send's bytes. BLE WSF's higher priority (49 vs 46) probably hides this in practice. | `APP_BleRingSendDataMsg` `0x004C4B7E` | `pc:ring-protocol-2026-09-30/README.md` |
| 2 | Queued ring TX carries no connection epoch, so a stale record can be sent after a reconnect that reuses the same numeric ID | `0x004C4910` | `pc:ring-tx-ownership-2026-10-01/README.md` |
| 3 | `RING_CmdTouchUpdate` checks `len > 7` but reads a u32 at offset 7 (an 11-byte read). The other ring RX handlers have no minimum-length guard. | `0x00472988` path | `pc:ring-protocol-2026-09-30/README.md` |
| 4 | The ESS audio heap record is freed before the WSF/ATT copy runs, so the second handoff uses a borrowed pointer | `0x0047538C` → `0x004BE24E` | `pc:audio-ble-metadata-2026-10-01/README.md` |
| 5 | The LC3 encoder's return value is ignored. On failure the firmware still sends 205 bytes with the metadata moved forward and zeros after it. The format has no validity flag. | `0x0057ADF8` | `pc:audio-stream-2026-10-01/README.md` |
| 6 | `attsProcMtuReq` raises peer MTU requests below 247 up to 247 | `0x0056C6FC` | `pc:ess-gatt-2026-10-01/README.md` |
| 7 | `SVC_PcmAppUnregister` does not check `source < 2`. Registration silently replaces the existing owner. | `0x0057ACD0`, `0x0057AB78` | `pc:audio-stream-2026-10-01/README.md` |
| 8 | Shutdown does not drain the WSF queue or stop TX producers. The ring acknowledges before deleting its queue, and the manager ignores an acknowledgement timeout. | `0x004C9778`, `0x004C53A6` | `pc:ring-allocator-lifecycle-2026-10-01/README.md` |
| 9 | Allocator size wrap: `WsfMsgAlloc(65528)` gets a 16-byte block. Separately, `align_up(UINT32_MAX)` becomes 0, so the request is serviced at the 12-byte minimum. | `0x004BF99E`, `0x004CFF42` | `pc:ring-allocator-lifecycle-2026-10-01/README.md`, `pc:shortcut-arm-tools-20261009-agent3/search-successor/REPORT.md` |
| 10 | NOR mode setup can treat a nonzero RDCR transport error as "true". The outer init then ignores the mode-setter result before QE. The `6C` read checks only the start address, not address + length. | `0x004704AC`, `0x0046FF40`, `0x00471020` | `pc:coverage-audit-parallel-2026-10-09/FLASH-ERROR-PATH-INDEPENDENT-REVIEW.md` |
| 11 | The UART channel-1 RX callback ignores how many bytes the 2,048-byte stream accepted. Flush then clears staging, so any rejected suffix is lost. | `0x005415E6`, `0x0055E4EC` | `pc:source-ledger-reconciliation-2026-10-09/REPORT.md` |
| 12 | The HCI LE-supported-states consumer copies 8 bytes without checking the length or the status byte | `0x00569B56` | `pc:fresh-provider-evidence-audit-20261009T192906Z/REPORT.md` |
| 13 | A security-event completion with an empty AES queue dereferences null: it reads at `0x34` from PC `0x0053628E` when no assert is compiled in | Cordio sec callback | `pc:coverage-audit-parallel-2026-10-09/security-encrypt-review-2026-10-10/REPORT.md` |
| 14 | The touch LP-history writer is unbounded; this was documented but no reachable overflow was shown | Touch ISR history | `pc:rescan-2026-10-08T125750Z/REPORT.md` |
| 15 | Misleading names and units in the firmware: `ble_msgtx_isConnected` actually tests fast mode; the wear duration is logged as "ms" but is in kernel ticks. The CCC-ready event 4 is not an acknowledgement. | — | §1 |

The ATT request guard was confirmed to match the newer SDK checks (method ≥ 18 is
rejected; length below the per-method minimum is rejected after the timer stop).
This is not a bug (`pc:coverage-audit-parallel-2026-10-09/att-guard-review/REPORT.md`).

## 7. Open blockers

- **Workflow.** The workflow is still `P2_EXECUTING`; G2–G6 have not run. The whole
  firmware needs P2 pseudocode, review and a corpus freeze before any C interface
  work.
- **Missing authentic inputs.**
  - IAR producer package (`.ewp`/ICF/map, `arm/src/lib`);
  - EM9305 v4.2 SDK and the MetaWare T-2022.09 project;
  - the vendor LOG2 extension specification or model;
  - NationalChip `lvp_tws` + compiler + model package;
  - target `.cycapsense` + generator;
  - case Keil project/flags;
  - private Ambiq HAL, Nema and Packetcraft sources;
  - resident ROM;
  - an external NOR dump.
- **Static questions still open.**
  - GX8002 CPU IRAM/DRAM alias visibility; DMA masking alone does not settle it.
  - I2S board mask bit 8: the initial mask 6 skips setup and no writer has been
    found.
  - Codec stored callback visibility.
  - The 177 resource-vs-envelope conflicts.
  - 404 L8 images not yet inspected.
  - Touch generated-data array sizes (LP history `0x2000065E..0x20000808`).
  - Touch constructor walker `0xA9E4`, exit `0xA9AC` (its extent overlaps memset),
    halt `0xAA40` and init stub `0xAA44`.
- **Hardware-only questions.** IRQ/PendSV delivery, DMA/cache coherence, MTU behavior
  of real peers, angle orientation (needs paired microphone vectors with known
  direction), and BQ27427 calibration.

## 8. Removed evidence and how to recover it

**`g2/analysis/` experiment directories.** These were bounded analysis batches,
each with a README/REPORT, `verify.py`/`probe.py`, `validation.json`,
disassembly, C pseudocode and host headers. They covered the ring, audio and ESS
batches; the shortcut-theory, frontier, tool and provider hunts; about 80
`rescan-*` progress snapshots; the coverage audit; source discovery; source and
replacement ledgers; assessments; and dashboard contracts. Several directories
held private Ghidra installs and projects, which were Git-ignored and are not in
the tag.

Recovery:

- One file: `git show pre-consolidation:g2/analysis/<dir>/<file>`.
- A whole directory: `git checkout pre-consolidation -- g2/analysis/<dir>`.
- List the tree: `git ls-tree -r --name-only pre-consolidation g2/analysis/<dir>`.

The `verify.py` scripts expect the locked blobs under `g2/blobs/official/` and the
Ghidra corpus under `g2/research/corpus/`. They also need Capstone 5.0.7 and
Unicorn 2.1.4 at `~/.local/share/opencfw/venv`.

**Paths still referenced by live tooling.** Restore these, or repoint the tools,
before relying on them:

| Removed path | Referenced by |
|---|---|
| `coverage-audit-parallel-2026-10-09/bundle-accounting-2026-10-13/full-accounting.json` | `tools/build/firmware_coverage.py` |
| `coverage-audit-parallel-2026-10-09/bundle-accounting-2026-10-13/resource-expansion/` | `tools/build/catalog_resources.py`, `tools/build/resources.json`, `tools/build/resource-inventory.json`, `resources/build_g2_catalog.py`, `resources/g2/s200-v2.2.6.10/manifest.json` |
| `rescan-2026-10-06T140235Z/instructions-current/` (LFS `instruction-ledger.jsonl`, about 184 MB) | `tools/build/catalog_disassembly.py`, `tools/build/disassembly-evidence.json`, `.gitattributes` |
| `shortcut-batch-2026-10-05/resources/extraction.json` | `g2/tools/manifests/g2-l8-resource-map.json` |
| `source-replacement-ledger-2026-10-08-readonly/mapped-readonly-data.json` | `resources/g2/s200-v2.2.6.10/manifest.json` |
| `shortcut-arm-tools-20261009-agent3/fff2-tail/REPORT.md`, `shortcut-source-gap-20261009-agent1/REPORT.md` | Citations in [protocols.md](protocols.md) §10; read them via `pre-consolidation:` |

**Top-level `reviews/`.** This held 1,812 independent P2 reviews named
`P2-<id|area>-<topic>-independent-review[-N]`, each with `001/{review.md, review.json,
fresh/}`. By area: about 470 touch, 80 Apollo, 27 C-SKY, 17 ARC and 3 case; the
rest are numbered clock/peripheral packets.

Each review re-ran a candidate packet's verifier under
`g2/build/pseudocode-first/20260930T190500Z/analysis/<packet>/<attempt>`. The
review checked body, literal-pool and table hashes against the locked image,
compared the decoded instructions, and recorded a verdict. The verdict was almost
always `PASS_SCOPED` with `accepted: false`. That means the instruction-level
behavior was confirmed, but none of the following was claimed: physical effect,
caller closure, or canonical admission. The reviews are campaign bookkeeping, not
admitted pseudocode.

Recovery:

- One review: `git show pre-consolidation:reviews/<dir>/001/review.md`.
- All reviews: `git checkout pre-consolidation -- reviews`.
- Index: `git ls-tree --name-only pre-consolidation reviews/`.
