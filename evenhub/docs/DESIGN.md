# OpenCFW EvenHub SDK — design

Status: draft / scaffold (2026-10-26). Code: `evenhub/src`, tests: `evenhub/test` (`node --test test/`).

## 1. Sources

| Source | What it gave us |
|---|---|
| Stock OTA `g2/blobs/official/g2-2.2.6.10`, `g2-2.3.2.14` | nanopb descriptors → authoritative field numbers and static sizes (`docs/schema-dump-*.txt`, `tools/dump_nanopb_desc.py`) |
| `g2/src/apollo-main/ui/a-25|a-26-evenhub-data-parser`, `a-14-evenhub-ui/evenhub_ui_page.c`, `a-28-evenhub-main`, `C3-evenhub-decompress`, `a-26-common-image-container` | cmd dispatch, validation, reply codes, image pipeline |
| `app/a-19-transport-protocol/transport_protocol_rx.c`, `g2/docs/reference/protocols.md` | 0xAA transport |
| `@evenrealities/even_hub_sdk` 0.0.16 (npm, 2026-09-24) + its docs | official API surface and documented limits |
| `~/Repo/evenrealitiesg2-swiftsdk` (fdadd7b) | community direct-BLE attempt (useful as a counter-example) |

## 2. Wire protocol as the firmware implements it

### 2.1 Transport (0xAA multipart)
8-byte header `AA | dst<<4|src | syncId | len | total | index(1-based) | serviceId | flags`.
Phone→glasses byte 1 = `0x21`. CRC-16/CCITT-FALSE (init 0xFFFF, poly 0x1021) over the whole
reassembled payload, little-endian, appended to the final packet (counted in its `len`).
Max payload 0x1000. Data per packet = ATT MTU − 11 (≤255). RX: 4 contexts, 1500 ms timeout.
Implemented in `src/transport.ts`; the encoder never splits the CRC across packets.

### 2.2 EvenHub service
Service ID **0xE0** (`EVENHUB_APP_ID`; replies/events go out via `Thread_MsgPbNotifyByBle(1, 0xE0, …)`).
Payload is one protobuf `EvenHub` message: `cmd` (tag 1), `magicRandom` (tag 2, echoed), and exactly one
oneof body whose tag is fixed per cmd. Full table: `src/schema.ts` / `proto/evenhub.proto`.

Firmware behaviour worth encoding in the SDK:
* **Create** is rejected when ≥2 containers have `isEventCapture`; >12 objects rejected; static caps 4 list / 8 text / 4 image.
* Every message is decoded into a 0x3758-byte struct and relayed raw to the other arm over UART — message size matters twice.
* Result codes are `EvenHub_ErrorCode_List` ordinals (create 0–3, image 4/5, rebuild 6/7, text 8/9, shutdown 10/11, heartbeat 12, audio 13/14).
* **Image**: payload must be a Windows 4-bpp BMP of exactly the container's w×h (palette → gray → L8). Optional RLE (`{count,byte}` pairs) or LZ4 *block*. Fragments are 0-based, strictly sequential, one ACK each. On the last fragment the firmware raises event 0x4C → decompress → `set_data`.
* **Firmware bug:** the receive buffer is w×h bytes and the first fragment copy is not bounds-checked. The SDK refuses any encoded image whose `totalSize` exceeds w×h.
* fw 2.3.x adds: create.menu(6), create.unknown7, rebuild.menu(5), text.textColor(14), textUpgrade.textColor(6), root tags 24–26.

## 3. Inefficiencies in the official SDK (evidence)

1. **Not a protocol SDK.** `even_hub_sdk` is obfuscated JS that only calls `window.flutter_inappwebview.callHandler(...)`; the Even app's Flutter code does the protobuf/BLE work. Apps can only run inside the Even app's WebView, need app ≥2.2.10, and every call pays JS→Dart→BLE hops.
2. **Images as JSON `number[]`.** `updateImageRawData` serializes pixel bytes as JSON arrays (~3.5–4× size inflation plus parse cost) before the app re-encodes them; audio PCM likewise as `number[]`/base64.
3. **No concurrent image sends** (documented): callers must serialize manually; the firmware actually supports pipelined fragments within one session only sequentially, so the SDK should own the queue.
4. **Rebuild flickers** (documented): the only way to change layout is a full rebuild; there is no diff. Text updates exist (`textContainerUpgrade`) but image/list need rebuild or full image push.
5. **Limits in prose, not enforced:** docs say width 20–288 / height 20–144, textColor 0–4, menu ≤10 / name ≤32 / id≠0, containerTotalNum 1–12 — errors surface as opaque firmware codes after a round trip. Real limits come from nanopb static sizes (e.g. text 999 B at create, 1999 B on upgrade; names 15 B; list 20×63 B).
6. **LZ4 only since 0.0.12** and no automatic choice of compression.
7. The **community Swift SDK** has wrong field numbers (no cmd/magic envelope; name at 13, content at 5, image data at 3) and uses ~174-byte fragments with fixed sleeps — it cannot work against this firmware as written.

## 4. Proposed architecture

```
 app code ── EvenHubClient (client.ts) ── messages.ts (encode/validate/decode)
                 │                            └── pb.ts (hand-written wire codec)
                 ├── image.ts (BMP4, RLE, LZ4, fragment planner, w×h cap)
                 └── transport.ts (0xAA fragment/reassemble, CRC) ── Link
 Link = { mtu, write(pkt), onPacket(cb) }  → Web Bluetooth | RN BLE | noble | simulator | WebView shim
```

* **Language: TypeScript, zero runtime deps.** Same audience as the official SDK (web apps), runs in browsers (Web Bluetooth), React Native and Node; Node ≥23.6 runs `.ts` directly so tests need no build. `erasableSyntaxOnly` keeps it strip-only.
* **Validation before send** against firmware rules (§2.2), throwing `EvenHubValidationError`.
* **Request/reply matching** on `(replyCmd, magic)`; events dispatched to `onEvent`.
* **Image pipeline**: `encodeBmp4` → auto-pick smallest of none/RLE/LZ4 → ≤4000-byte fragments (keeps the whole pb message under the 0x1000 TPL cap) → serialized per-client queue, stop-and-wait ACKs, status 5 aborts.
* **Version flag (todo)**: fw 2.3 fields are emitted only when set; a `firmware: '2.2'|'2.3'` option should reject them on 2.2.
* **API sketch**
  ```ts
  const hub = new EvenHubClient(link, { onEvent });
  await hub.createPage({ texts: [{ x:0,y:0,width:576,height:288,containerID:1,content:'Hi',isEventCapture:true }] });
  await hub.updateText({ containerID: 1, content: 'Hello' });
  await hub.updateImage({ containerID: 2, width: 288, height: 144, bmp: encodeBmp4(gray, 288, 144) });
  await hub.shutdown();
  ```

## 5. Open questions
1. **Service byte.** Firmware uses 0xE0; the Swift SDK sends "0x0E-20" (service 0x0E = health in protocols.md, flags 0x20). Needs one on-device capture. Configurable via `serviceId`.
2. **Direct BLE vs WebView.** Direct BLE requires the Even app not to hold the link (and pairing/auth handshake, not yet covered). A `Link` backed by the official `callEvenApp` bridge would give compatibility but inherit its overhead.
3. **Unknown fields:** zOrder tags (inferred), create tag 7, root tags 24–26, menu item tags 3/5.
4. Whether the firmware echoes `magicRandom` on *every* reply (assumed; image ACK path confirmed in source).
5. Pipelining multiple fragments before ACK — not attempted; firmware is stop-and-wait.
6. Simulator integration test once the g2 simulator exposes a BLE/TPL socket.

## 6. Direct Bluetooth connection (replacing the Even app)

Addresses below are stock 2.2.6.10 run addresses (file offset + 0x437FE0) unless noted.
✅ = read from firmware code/data. 🟡 = firmware plus community captures agree. ❓ = needs a real-device capture.

### 6.1 GATT (attsAttr_t table 0x6de974..0x6deb44, 16-byte records; UUID constants 0x7894a0..0x789580)
UUID base `00002760-08c2-11e1-9073-0e8ac72eXXXX` ✅ (2.3.2.14 constants at 0x7e96b8; it adds char 5403, write, handle 0x0847).

| Service | Chars (props) | Value handles | Role |
|---|---|---|---|
| EUS 5450 | 5401 write-no-rsp, 5402 notify | 0x0842 / 0x0844 | **TPL protocol** (eusWriteCallback 0x4bdf3c → TPL_ReceivePacket pipe 0) ✅ |
| ESS 6450 | 6401 / 6402 | 0x0862 / 0x0864 | ESS data ✅ |
| EFS 7450 | 7401 / 7402 | 0x0882 / 0x0884 | file transport ✅ |
| OTA 1001 | 0001 / 0002 | 0x0822 / 0x0824 | OTA ✅ |
| NUS 6E400001 | std | 0x08a2 / 0x08a4 | production test ✅ |

Value perms are 0x10 (no encryption needed at the ATT level); CCC perms are 0x11 ✅.

### 6.2 Bonding (smpCfg 0x774D44 = `b80b0000 03 07 10 03 01`)
NoInputNoOutput, key 7–16, 3 attempts, auth 0x01 (bonding, no MITM, no SC) ⇒ legacy **Just Works** ✅. The peripheral starts a security request (APP_SlaveStartSecurityRequestEvent 0x46effc) ✅. The OS completes pairing; the SDK does nothing. Web Bluetooth/CoreBluetooth behaviour ❓.

### 6.3 App-level auth: devcfg service 0x80 (nanopb 0x7766dc, APP_PbRxDevCfgFrameDataProcess 0x4d83d8)
There is **no key exchange and no crypto**: security is BLE bonding plus a SecAuth flag ✅.
1. `cmd 4 / tag 3 SecAuth{1 secAuth=1, 2 phoneType}`. PB_RxSecAuth 0x4bb3dc stores phoneType; if the link is not yet encrypted (0x20074ffc) it waits. Immediate reply PB_TxEncodeSecAuth 0x4bb576 **echoes magic** ✅. After encryption, NotifySecAuth 0x4bb92c/0x4bb73a (+100 ms, +2 s) sends cmd 4 with **magic = tick count (not an echo)** ✅. phoneType 4 is from captures 🟡 (firmware comment suggests 3 = iOS ❓). TPL flags 0x00 on this packet follow captures 🟡.
2. `cmd 5 / tag 4 PipeRole{1 asCmdRole}`; captures send 2 then 1 🟡; meaning of values ❓.
3. `cmd 0x80 / tag 128 TimeSync{1 utc u32, 2 tz int8, 3 u8}` (0x5435de): sets the clock, RPCs the other arm, RPC_SystemBleStatusSync(1) ✅. Captures put int64 -24 (10-byte varint) in field 3, which exceeds the u8 range; SDK `compatTxid` (default on) reproduces the captured bytes 🟡. Whether nanopb rejects it ❓.
4. Keepalive `cmd 0x0E / tag 13` (0x543378): RPC_SystemBleStatusSync(1) and re-arms a 30 s timer (0x4b81b8, which in the reconstruction only logs) ✅. The SDK sends it every 15 s; necessity ❓.
5. Unknown cmd ⇒ cmd 10 ErrorCode{code 8 NOT_SUPPORT} ✅. GET_DEVICE_INFO (12) has **no handler** in 2.2.6.10 ✅.

### 6.4 Version negotiation: setting service 0x09 (nanopb 0x77772c)
Request `{1 cmd≠0, 2 magic u32 (must differ from the last one, setting_duplicate 0x49b198), 4 {}}` ✅. setting_parse_data_package 0x49b1f8 → setting_data_recv_handler 0x466976 (kind 4) → setting_respond_with_local_data 0x49ba58/0x49b7c4. Only the master arm (role 1) answers, and only if cmd≠0 ✅. Reply `{1:2, 2:echoed magic, 4:{…}}` built by setting_build_full_status_package 0x49b4da: **tag 5 = left version** (config+0x44; empty on the first ask while it is fetched from the slave, 0x46ba02), **tag 6 = right version** (ROM 0x78b7bc "2.2.6.10") ✅. The SDK retries once if left is empty and picks '2.2'/'2.3' from the right version. 2.2 rejects menu containers. The advertising name template is "0Even G2_**_#_A" (0x359a70); field meaning ❓.

### 6.5 Magic echo (EvenHub 0xE0)
Every synchronous EvenHub reply echoes the request magicRandom ✅. All reply paths call evenhub_send_reply 0x4d9c86 / image 0x4da4a4 / IMU 0x4da60c with `msg->seq`, both in the parser (a-26, evenhub_data_parser) and in the UI page code (a-14 evenhub_ui_page.c). Exceptions: **heartbeat and audio-control send no reply when the EvenHub app is not running**, and system events (evenhub_send_system_event 0x4d9d9a) use seq 0. devcfg replies echo; NotifySecAuth does not; setting echoes the 32-bit magic.

### 6.6 SDK flow (`connect()` in src/session.ts)
Transport (requestG2 / connectNode): connect → EUS → CCC 5402 on → OS bonding. Then SecAuth → PipeRole → TimeSync → setting status → firmware line → heartbeat timer → `EvenHubClient` sharing one TPL sync counter.

### 6.7 Needs a real-device capture
Service-id 0xE0 on the wire; single link (right arm) vs both arms; phoneType/pipe-role meaning; TimeSync field 3 tolerance and tz unit; whether the right arm's tag 5/6 strings arrive as expected; advert name side marker; heartbeat necessity and the disconnect timer; Web Bluetooth pairing prompt and real MTU (assumed 247).
