# Cordio / Packetcraft BLE Host Stack — Identity & Version Audit

Status: research-only identification

Scope: identify and version the BLE **host** stack in the Even Realities G2
Apollo510 main image. The EM9305 is a separate BLE **controller** (linked over
HCI) and is out of scope except where it defines the host/controller boundary.

## Target

- Blob: `blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin`
  (3,523,396 bytes / 0x35C004)
- Format: raw ARM Cortex-M55 Thumb-2 XIP image.
- Load base: `run = file_offset + 0x00437FE0` (confirmed: file 0x20 -> run
  0x438000). All run addresses below are computed with this offset and verified
  to disassemble as valid Thumb-2 (see "Disassembly spot-check").

## 1. Stack identity — Cordio (Packetcraft) BLE host

**Conclusion: the host stack is the Arm Cordio / Packetcraft BLE host, bundled
via AmbiqSuite for the Apollo510.** This is proven by retained build-tree source
paths embedded as `__FILE__` literals for WSF assert/trace. Every path lives
under `third_party\cordio\` in the vendor build tree
`D:\01_workspace\s200_ap510b_iar_git\` (Apollo510b, IAR toolchain).

The three canonical Cordio components are all present:

| Cordio component | Source subtree (in image) | Meaning |
|---|---|---|
| WSF | `third_party\cordio\wsf\sources\port\freertos\...` | Wireless Software Foundation, ported onto FreeRTOS |
| BLE host | `third_party\cordio\ble-host\sources\{stack,hci}\...` | ATT / L2CAP / DM / SMP + HCI |
| BLE profiles / app fwk | `third_party\cordio\ble-profiles\sources\apps\app\...` | Cordio application framework |

The HCI source lives under `ble-host\sources\hci\ambiq\` — the **AmbiqSuite HCI
port**, which is the packaging Ambiq ships for its Cordio integration.

Every source-path string is referenced from the code (`.text`) region via
literal pools — i.e. these modules are compiled in, not leftover data. Example
literal-pool references (file offsets, all inside `.text` 0x40000–0x136000):

| Module | string run addr | code literal-pool ref (file off) |
|---|---|---|
| `app_db.c` | 0x006D84BC | 0x409A0, 0x41590, 0x42300 |
| `att_main.c` | 0x006DC754 | 0x7D1F8 |
| `atts_csf.c` | 0x006DC934 | 0xF50A8, 0xF5A4C |
| `l2c_main.c` | 0x006DD4D4 | 0xF8BA0 |
| `dm_conn.c` | 0x006DFFB4 | 0x7E54C, 0x7E808, 0x7F480 |
| `hci_evt.c` | 0x006E0518 | 0x13339C, 0x133804 |
| `smp_db.c` | 0x006E19F0 | 0x10A978 |
| `smp_sc_main.c` | 0x006DE8B4 | 0x135858 |
| `wsf_buf.c` | 0x006E20C4 | 0xF8548 |

## 2. Subsystems present (with run addresses)

Run address = file offset of the `__FILE__` string + 0x437FE0.

### WSF (Wireless Software Foundation) — FreeRTOS port
| File | file off | run addr |
|---|---|---|
| `wsf\...\port\freertos\wsf_assert.c` | 0x2A6FF4 | 0x006DEFD4 |
| `wsf\...\port\freertos\wsf_timer.c` | 0x2A7054 | 0x006DF034 |
| `wsf\...\port\freertos\wsf_trace.c` | 0x2A70B4 | 0x006DF094 |
| `wsf\...\port\freertos\wsf_buf.c` | 0x2AA0E4 | 0x006E20C4 |

### HCI (AmbiqSuite port — talks to EM9305 controller)
| File | file off | run addr |
|---|---|---|
| `ble-host\sources\hci\ambiq\hci_evt.c` | 0x2A8538 | 0x006E0518 |

### DM (Device Manager)
| File | file off | run addr |
|---|---|---|
| `stack\dm\dm_adv_leg.c` | 0x2A50D4 | 0x006D90B4 |
| `stack\dm\dm_conn_sm.c` | 0x2A5134 | 0x006D9114 |
| `stack\dm\dm_conn.c` | 0x2A7FD4 | 0x006DFFB4 |
| `stack\dm\dm_dev.c` | 0x2A8030 | 0x006E0010 |

Runtime trace strings confirm the DM connection state machine is live, e.g.
`dmConnSmExecute event=%d, action = %d, next state = %d` (run 0x0071DFB8),
`dmConnUpdExecute: Invalid action set ID: %d` (run 0x0073E004).

### L2CAP
| File | file off | run addr |
|---|---|---|
| `stack\l2c\l2c_main.c` | 0x2A54F4 | 0x006DD4D4 |
| `stack\l2c\l2c_master.c` | 0x2A5554 | 0x006DD534 |
| `stack\l2c\l2c_slave.c` | 0x2A55B4 | 0x006DD594 |

### ATT / GATT server + client
| File | file off | run addr |
|---|---|---|
| `stack\att\att_main.c` | 0x2A4774 | 0x006DC754 |
| `stack\att\attc_disc.c` | 0x2A47D4 | 0x006DC7B4 |
| `stack\att\attc_main.c` | 0x2A4834 | 0x006DC814 |
| `stack\att\attc_proc.c` | 0x2A4894 | 0x006DC874 |
| `stack\att\atts_ccc.c` | 0x2A48F4 | 0x006DC8D4 |
| `stack\att\atts_csf.c` | 0x2A4954 | 0x006DC934 |
| `stack\att\atts_ind.c` | 0x2A49B4 | 0x006DC994 |
| `stack\att\atts_main.c` | 0x2A4A14 | 0x006DC9F4 |
| `stack\att\atts_proc.c` | 0x2A4A74 | 0x006DCA54 |
| `stack\att\atts_sign.c` | 0x2A4AD4 | 0x006DCAB4 |

### SMP (Security Manager) — incl. LE Secure Connections
| File | file off | run addr |
|---|---|---|
| `stack\smp\smp_main.c` | 0x2A6874 | 0x006DE854 |
| `stack\smp\smp_sc_main.c` | 0x2A68D4 | 0x006DE8B4 |
| `stack\smp\smpr_act.c` | 0x2A6934 | 0x006DE914 |
| `stack\smp\smp_act.c` | 0x2A99B4 | 0x006E1994 |
| `stack\smp\smp_db.c` | 0x2A9A10 | 0x006E19F0 |

### Cordio application framework (ble-profiles)
| File | file off | run addr |
|---|---|---|
| `apps\app\app_main.c` | 0x2A4714 | 0x006DC6F4 |
| `apps\app\app_master.c` | 0x2A20B8 | 0x006DA098 |
| `apps\app\app_master_leg.c` | 0x2A0614 | 0x006D85F4 |
| `apps\app\app_slave.c` | 0x2A2180 | 0x006DA160 |
| `apps\app\app_slave_leg.c` | 0x2A067C | 0x006D865C |
| `apps\app\app_server.c` | 0x2A211C | 0x006DA0FC |
| `apps\app\app_disc.c` | 0x2A46B4 | 0x006DC694 |
| `apps\app\common\app_db.c` | 0x2A04DC | 0x006D84BC |
| `apps\app\common\app_ui.c` | 0x2A06E4 | 0x006D86C4 |

GATT (the profile layer) is present but sits in the G2 glue (`platform\ble\
profiles\gatt\profile_gatt.c`), not as a stock Cordio `svc_*`/`gatt/` module —
see §4.

### Disassembly spot-check
Capstone (Thumb, M-class) at the `att_main.c` region decodes cleanly as a normal
Cortex-M ARM-EABI function, e.g. at run 0x004B5014:
`push {r7, lr}` / `ldr r3,[pc,#0x1d0]` / … / `pop {r1, pc}`, with a following
`push {r3,r4,r5,lr}` prologue at 0x004B503C. This confirms both the load base and
that the referenced Cordio modules are real compiled functions.

## 3. AmbiqSuite 5.1.0 correlation

Consistent-with (not yet byte-proven) the AmbiqSuite-5.1.0-bundled host:

- **Packaging matches Ambiq's Cordio layout exactly**: `third_party/cordio/`
  split into `wsf` + `ble-host` + `ble-profiles`, an `hci/ambiq/` transport
  port, and a `wsf/sources/port/freertos/` OS port. This tree shape is how
  AmbiqSuite ships Cordio for Apollo-class parts.
- Target is Apollo510b (`s200_ap510b_iar_git`), the Apollo5 family that ships
  AmbiqSuite 5.1.0 — matching the stated context.
- Feature set is Bluetooth 5.x host: `atts_csf.c` (ATT Client Supported
  Features / robust caching, BT 5.1), `atts_sign.c` (signed writes),
  `smp_sc_main.c` (LE Secure Connections), and both legacy + extended DM/app
  variants (`*_leg.c` alongside non-legacy).

What is NOT yet established: an exact equality to the AmbiqSuite 5.1.0 tree.
No AmbiqSuite 5.1.0 reference source was diffed in this pass; the correlation
rests on layout + feature evidence, not a byte/function-hash match.

## 4. G2-specific glue boundary (application / database on top of Cordio)

Everything under `platform\ble\` and `platform\protocols\` is Even Realities
code layered on the stock Cordio framework — this is where G2 app/database
changes live, distinct from the normalized upstream host.

BLE application layer — `platform\ble\` (run addrs):
- `app_ble.c` 0x00711D94, `app_ble_central.c` 0x006FF9B8,
  `app_ble_peripheral.c` 0x006F809C, `app_ble_discovery.c` 0x006F7FC4,
  `app_connect_params.c` 0x006F81BC, `app_ble_peer_mgr.c` 0x006FFF4C.

G2 custom GATT services — `platform\ble\profiles\*\profile_*.c`:
- `ancc` (Apple Notification Center client), `gatt`, `nus` (Nordic-UART-style
  transport), `ota`, `ring`, `ess` (env sensing), `efs`, `eus`. These are the
  G2 service database, layered on Cordio ATTS.

Application protocol services — `platform\protocols\pb_service_*` (protobuf over
a TinyFrame `transport_protocol.c`): `even_ai`, `health`, `teleprompt`,
`translate`, `notification`, `dashboard`, `dev_config`/`pair_mgr`, `quicklist`,
`terminal`, `ring`, `setting`, `onboarding`, `conversate`, `glasses_case`.

**Pairing / bonding record database** — the boundary the memory map calls the
"MRAM record database": Cordio's stock `app_db.c` (0x006D84BC) and `smp_db.c`
(0x006E19F0) provide the bonding-DB API, and G2's `app_ble_peer_mgr.c`
(0x006FFF4C) plus `pb_service_pair_mgr.c` persist/manage those records (to MRAM).
This is the primary place where G2 app-database code replaces/wraps the stock
Cordio NVM/database functions.

Host/controller boundary: the Apollo510 runs the **host** (above); the **EM9305**
is the **controller**, reached over HCI (`hci/ambiq/`). Separate G2 driver /
DFU code drives the controller image: `am_devices_em9305_init` (run 0x0071F5D0),
`platform\service\DFU\service_em9305_dfu.c` (0x006EF818), with
`[srv.em9305]` firmware-header logging. The controller firmware
(`firmware_ble_em9305.bin`) is out of scope for host identification.

## 5. Version determination

- **Family**: Arm Cordio / Packetcraft BLE **host** stack. Definitive
  (source-path evidence, §1). The retained folder name is `cordio` (Ambiq keeps
  the historical name even post-Packetcraft rebrand).
- **Bundling**: shipped via AmbiqSuite for Apollo510b (Apollo5 → AmbiqSuite
  5.1.0 per context). Strongly consistent (§3), not byte-proven.
- **Exact Cordio release number: NOT pinned.** The host modules carry no
  embedded version constant string (unlike the controller's `LlGetVersion`,
  which is on the EM9305, not this image). Feature evidence bounds it to a
  Bluetooth-5.1-era host (robust caching / CSF present) but does not yield a
  precise `rNN.NN`.

Not guessed: I am explicitly not asserting a specific Cordio `rNN` release.

## 6. Current source-lineage result

The focused follow-on audit in `cordio-version-recovery-audit.md` now proves
two independent r20.05-or-later semantics: the ATT client-supported-features
write transition and the eight-event DM connection state machine. The audited
public source blobs are identical from Packetcraft r20.05 through r20.05c,
making that interval a defensible bounded source oracle for those functions.

It does **not** prove one exact whole Cordio tree. G2's Ambiq FreeRTOS WSF
port has different source-line markers from the public AmbiqSuite 4.5 mirror,
and its DM trace/body contains local instrumentation. The authenticated local
AmbiqSuite 5.1.0 snapshot covers HAL inputs only and cannot authenticate the
portal-restricted Cordio archive. Source reuse should therefore select
Apache-2.0 r20.05c explicitly and promote functions one at a time after ABI,
configuration, and closure proof, not replace the full BLE stack wholesale.

## 7. Remaining checks to settle exact vendor tree

1. Obtain AmbiqSuite 5.1.0 `third_party/cordio` source and diff module list +
   function-level structure (function-hash / prologue-signature match) against
   the modules enumerated here — this would upgrade §3 from "consistent" to
   "confirmed" and can back out the underlying Cordio/Packetcraft release.
2. Check the AmbiqSuite 5.1.0 release notes / `cordio` `VERSION`/changelog for
   the pinned Packetcraft host revision, then confirm by presence/absence of
   modules that changed between revisions (e.g. `atts_csf.c`, `atts_dyn.c`).
3. Cross-read the EM9305 controller image's `LlGetVersion` / HCI
   `Read_Local_Version` build for the controller-side revision (separate blob),
   to corroborate the host generation.
4. Confirm the MRAM bonding-DB seam by disassembling `app_db.c` /
   `app_ble_peer_mgr.c` entry points (literal-pool refs at file 0x409A0 /
   0x41590 / 0x42300 for `app_db.c`) to document which stock Cordio DB functions
   G2 replaced with MRAM-backed implementations.

## Evidence commands (reproducible)

```
strings -a -t x <blob> | grep -iE 'cordio'          # source-path proof
# run = fileoff + 0x437FE0
# literal-pool xref: search image for little-endian <run addr> of each __FILE__
```
