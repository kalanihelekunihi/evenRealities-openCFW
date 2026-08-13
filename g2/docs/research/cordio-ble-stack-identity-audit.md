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

The focused [HCI event recovery](cordio-hci-evt-source-recovery.md) now closes
this proprietary translation unit without copying its source: 79 of the 80
official Ambiq R4.4.1 source-family functions are linked, with only
`hciEvtGetStats` dead-stripped. Stock's 85-entry parser and callback-size
tables exactly match that later official layout, and the complete 6,816-byte
physical interval, ten direct calls, and 74 stored parser pointers are pinned.
This is exact reconstruction-oracle corroboration, not a claim that the later
R4.4.1 import was G2's historical producing commit.

The adjacent [HCI core recovery](cordio-hci-core-source-recovery.md) closes
the proprietary transport/control object without requiring a retained source
path. Its 22 linked definitions, 32 direct calls, 64-bit LE-feature API, six
CIS records, and exact global/literal closure select the same later R4-era
architecture. Two APIs are source-only. Stock omits the later neuralSPOT ACL
send delay and nsx priority/trace additions, so the result is deliberately
classified as a source-family and ABI match rather than whole-file identity.

The [HCI platform-shim recovery](cordio-hci-core-ps-source-recovery.md)
extends that closure through `[0x00530C00,0x00530D74)`. Its nine linked
functions expose the same `hciCoreCb`/`hciCb` ownership, a true 64-bit feature
getter, and a separate ISO receive callback. Eleven unused getters are
source-only. These facts independently select the proprietary R4-era family
over AmbiqSuite R2.5.1.

The [HCI transport recovery](cordio-hci-tr-source-recovery.md) closes the
driver-facing object at `[0x0053013C,0x00530364)`: three linked functions,
one source-only getter, four exact callers, and the complete seven-variable
receive state. Stock returns send status without freeing or completing the
buffer and applies the later receive validation, excluding R2.5.1 and
selecting the same R4-era proprietary family.

The [shared HCI command recovery](cordio-hci-cmd-source-recovery.md) closes
the adjoining 2,668-byte proprietary object: 50 linked definitions, 22
source-only definitions, 156 direct ingress sites, 127 body call sites, and
the complete command queue/timer ABI. Its later 72-definition R4 inventory is
an exact reconstruction oracle, while the historical producing commit remains
unresolved and no proprietary implementation bytes are imported.

The adjacent [HCI PHY-command recovery](cordio-hci-cmd-phy-source-recovery.md)
accounts for its complete three-definition Apache source inventory. Only
`HciLeSetPhyCmd` links; its exact `0x2032` command encoding is rooted by the
closed DM PHY wrapper. The read and set-default command APIs are source-only.

The complementary [optional-command exclusion](cordio-hci-optional-command-exclusion.md)
classifies all 57 definitions across the AE, BIS, CIS, CTE, ISO, and PAST
command TUs as source-only. Each wrapper requires one allocator call, while
the closed stock allocator census leaves no caller outside the shared and PHY
command objects.

The [Apollo3 HCI-driver recovery](cordio-hci-driver-source-recovery.md) closes
the hardware-facing boundary as 12 linked and four source-only definitions.
The 30 exact calls, 66 provider calls, blocking queue/RX ABI, and sole stored
WSF handler pointer are pinned without accepting an interior target. Unlike
the HCI source files above, this driver is not one coherent archived revision:
its Apollo3 radio path, later null-safe handler, and Cooper-era vendor-command
tail require a mixed-version Ambiq classification. The later official imports
are behavioral corroboration rather than historical producing-commit pins.

The [product BLE-startup recovery](g2-app-ble-startup-recovery.md) closes the
boundary above that driver: twelve product bodies close the callback/message
state machine, initialize WSF and the full active Cordio handler chain,
register services, boot the radio, and schedule delayed work. A thirteenth
adjacent body is not product BLE code at all:
vector slot 75 maps it to Apollo510 `GPIO0_607F_IRQn`. This exact vector proof
corrects the earlier assumption that `HciDrvIntService` had an interrupt
caller outside the OTA. The service is retained but statically unrooted; the
GPIO wrapper does not call it.

The [vendor reset-sequence recovery](cordio-hci-vs-reset-sequence-recovery.md)
then closes the controller initialization state machine. Four functions link
and four hooks are source-only. Stock's Reset/address -> NVDS -> RF-power ->
standard discovery chain is a product-specific blend of the Apollo3 and
Cooper layouts, which explains the newer driver helpers without promoting
either later official import to a whole-file or historical identity claim.

### DM (Device Manager)
| File | file off | run addr |
|---|---|---|
| `stack\dm\dm_adv_leg.c` | 0x2A50D4 | 0x006DD0B4 |
| `stack\dm\dm_conn_sm.c` | 0x2A5134 | 0x006D9114 |
| `stack\dm\dm_conn.c` | 0x2A7FD4 | 0x006DFFB4 |
| `stack\dm\dm_dev.c` | 0x2A8030 | 0x006E0010 |

Runtime trace strings confirm the DM connection state machine is live, e.g.
`dmConnSmExecute event=%d, action = %d, next state = %d` (run 0x0071DFB8),
`dmConnUpdExecute: Invalid action set ID: %d` (run 0x0073E004).

The `dm_dev.c` path is now bound to a complete 672-byte stock translation
unit containing twelve linked functions / 626 code bytes, three registered
interface/action pointers, and 29 direct calls. Its 21-component, three-bit
message ABI and vendor-command translation align with the official Ambiq
R4.4.1 source family. See the
[DM local-device recovery](cordio-dm-dev-source-recovery.md).

The neighboring optional `dm_dev_priv.c` has no retained path because it is
not linked. The decoded 21-entry boot interface table leaves component 1 on
`dmFcnDefault`; all table-base references and component installs are closed,
with no slot-1 write or privacy action/interface table. See the
[DM device-privacy exclusion](cordio-dm-dev-priv-exclusion.md).

`dm_main.c` itself has no retained path string, but its immutable data is a
stronger discriminator: stock has exactly 90 HCI routes, 92 callback lengths,
and 21 component slots. Only the official AmbiqSuite R4.4.1 family has that
combination; r19, AmbiqSuite 2.5.1, and public r20 do not. All sixteen stock
functions are independently bounded. See the
[DM main-router recovery](cordio-dm-main-source-recovery.md).

The neighboring pathless `dm_priv.c` object supplies a second architectural
pin: its component-6 seven-action table and separate component-15 two-action
AES table are the Packetcraft r20/Ambiq R4 split, not the r19/AmbiqSuite 2.x
nine-action layout. Twenty-one bodies survive and four public APIs are
dead-stripped. See the [DM privacy recovery](cordio-dm-priv-source-recovery.md).

The adjacent `dm_sec.c` object provides a behavioral r20/R4 lower bound:
stock rejects nonzero EDIV/Rand LTK requests while LESC is enabled, a branch
absent from r19/AmbiqSuite 2.x. Its eight linked functions, four dead APIs,
and component-5 interface are fully bounded. See the
[DM security recovery](cordio-dm-sec-source-recovery.md).

The component-9 `dm_phy.c` initializer supplies an independent ABI lower
bound: stock calls the widened 64-bit `HciSetLeSupFeat` form with mask
`0x900` under the task lock. That exact r20/R4 body excludes the older
r19/AmbiqSuite 2.x initializer. See the
[DM PHY recovery](cordio-dm-phy-source-recovery.md).

All three `dm_sec_slave.c` API wrappers also survive. Their source bodies are
release-invariant, but the retained LTK-response wrapper writes event `0x29`,
not the r19/AmbiqSuite 2.x value `0x51`, independently confirming the r20/R4
message-ID layout. See the
[DM slave-security recovery](cordio-dm-sec-slave-source-recovery.md).

The master connection manager supplies the direct architectural proof:
`DmL2cConnUpdateInd` emits component-14 event `0x72` and enters
`dmConnUpdExecute`, not the r19 unified connection state machine. See the
[DM master-connection recovery](cordio-dm-conn-master-source-recovery.md).

The linked legacy-master initializer independently matches that split: it
installs separate two-entry main/update action tables under the task lock,
where r19 used a single unlocked four-entry table. See the
[legacy-master recovery](cordio-dm-conn-master-leg-source-recovery.md).

The linked legacy-slave initializer supplies the symmetric proof: it installs
a four-entry main table plus the separate two-entry slave update table under
the task lock, whereas r19 used one unlocked six-entry table. See the
[legacy-slave recovery](cordio-dm-conn-slave-leg-source-recovery.md).

The core slave connection unit completes that route: its update-confirmation
bridge emits component-14 event `0x73` and enters `dmConnUpdExecute`, with an
exact two-entry update table. See the
[slave-connection recovery](cordio-dm-conn-slave-source-recovery.md).

The linked L2CAP slave object independently selects the same generation: it
validates HCI handles through `DmConnIdByHandle` and indexes state by
`connId-1`, while r19/AmbiqSuite 2.x indexes directly by handle. See the
[L2CAP slave recovery](cordio-l2c-slave-source-recovery.md).

All three L2CAP master functions are also linked. Their public bodies are
invariant across r19/r20, so they corroborate exact Cordio definitions but
do not add an independent release discriminator. See the
[L2CAP master recovery](cordio-l2c-master-source-recovery.md).

All 11 L2CAP core definitions are linked in the corrected object ending at
`0x00530C00`. The initializer supplies six exact callback entries, and the
public bodies are likewise invariant across r19/r20. See the
[L2CAP core recovery](cordio-l2c-main-source-recovery.md).

The optional connection-oriented-channel unit is not linked. Its mandatory
callback replacement and DM registration are absent, accounting for all 67
`l2c_coc.c` definitions as source-only. See the
[L2CAP CoC exclusion](cordio-l2c-coc-exclusion.md).

The secure-connections main object is fully bounded at
`[0x0056CDC0,0x0056D8C4)`: 18 linked definitions / 2,626 code bytes and four
dead APIs. Its event-name switch includes r20's cleanup value `0x1F`, while the
r19/AmbiqSuite 2.x source does not. One hundred eleven exact-entry calls and
zero real interior ingress close the module. See the
[SMP secure-connections main recovery](cordio-smp-sc-main-source-recovery.md).

The paired secure-connections role machines are also complete: four functions
/ 598 code bytes, two code/pool objects, two interfaces, 106 action pointers,
78 state pointers, and all 80 state tables. Stock's responder carries r20's
extra timeout action and cleanup transition. See the
[SMP SC state-machine recovery](cordio-smp-sc-state-machines-source-recovery.md).

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

These nine paths are now traced specifically to AmbiqSuite's Apache-2.0 Cordio
application fork. The selected public source is AmbiqSuiteSDK 2.5.1 commit
`de5c6ba3044f4ef0f0c907c3f83fbbaa5795262f`, not pristine Packetcraft and not
the unknown private G2 producing checkout. Fifty path-anchored functions /
29,110 bytes and the complete 14-function legacy master/slave clusters are
pinned by the [focused source recovery](ambiqsuite-cordio-app-framework-source-recovery.md).

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
- **Release interval**: independent ATT/SMP discriminators require Packetcraft
  **r20.05-or-later** semantics; the relevant public blobs are invariant
  through r20.05c. This bounds a public source-oracle interval but does not
  prove a pristine whole-tree checkout or one patch letter.
- **Vendor fork**: common and legacy advertising use Ambiq's inline
  flexible-array message ABI, while public Packetcraft r19/r20 uses a pointer
  field. The DM connection manager uses the r20 separated update/peer-SCA
  architecture while retaining AmbiqSuite 2.5.1 warning suppression and
  product validation additions. The WSF FreeRTOS ports and product diagnostics
  carry further deltas.

## 6. Current source-lineage result

The focused follow-on audits prove r20.05-or-later semantics through ATT
client-supported-features, ATT CCC, ATT discovery, and the SMP message enum.
The audited public source blobs are identical from Packetcraft r20.05 through
r20.05c, making that interval a defensible bounded source oracle. The common
advertising producer and legacy consumer independently prove Ambiq's inline
flexible-array payload ABI at message offset `+8`.

It does **not** prove one exact whole Cordio tree. G2's Ambiq FreeRTOS WSF
port has different source-line markers from the public AmbiqSuite 4.5 mirror,
and its DM trace/body contains local instrumentation. The authenticated local
AmbiqSuite 5.1.0 snapshot covers HAL inputs only and cannot authenticate the
portal-restricted Cordio archive. Source reuse should therefore select
Apache-2.0 r20.05c explicitly and promote functions one at a time after ABI,
configuration, and closure proof, not replace the full BLE stack wholesale.

The completed `smp_main.c` audit sharpens that boundary. Stock combines the
Packetcraft r20 `keyReady`/LESC API with an AmbiqSuite 2.5.1 stale-AES queue
cleanup that never appeared in the public r20 file. All twenty linked
functions are bounded, and the hybrid builds with zero unresolved providers,
but retained line constants still prove minor downstream text drift. This is
direct evidence of a rebased vendor patch stack: r20.05-family public behavior
is the correct base, while neither pristine Packetcraft r20 nor pristine
AmbiqSuite 2.5.1 is the exact whole-tree answer.

The adjacent `smp_sc_main.c` audit provides a cleaner release discriminator.
Its 18 linked definitions use the invariant Packetcraft r20.05--r20.05c public
bodies, and the retained cleanup-event string at `0x1F` excludes the r19
message enum. Four unused public definitions are dead-stripped. Unlike the
hybrid `smp_main.c`, this object needs no semantic source patch; compiler and
product placement identity remain separate from the exact source-family match.

The role-specific SC state machines reinforce that pin using executable
dispatch data rather than diagnostic strings alone. The initiator is
release-invariant, while the responder's 55-entry action table and exact
timeout/cleanup rows match r20.05--r20.05c and exclude the 54-action r19/Ambiq
layout. All rooted tables are traversed and hashed, so the conclusion does not
depend on names or neighboring code placement.

The shared `smp_act.c` object closes the execution layer beneath all four role
tables. Stock links all 25 public definitions, including the r20-only
security-request-timeout action, and uses the later guarded SC trace path.
Four action tables and two callback pairs account for all 62 stored entry
pointers; 78 direct calls also land only at exact entries. This independently
selects the r20.05 family and leaves no opaque common SMP action body.

The ATT client core independently selects the same generation. Its stock
control block contains three bearers for each of three connections, and its
17-entry request table uses the r20 EATT architecture. Twenty of 21 source
definitions link; the only stripped API is `AttcSetAutoConfirm`. The receive
callback also implements the zero-length check found in the later official
Ambiq R4.4.1 source, while local validation/logger expansion prevents an exact
whole-source-text claim. All 32 direct calls and 17 stored entries land at
exact function starts.

The completed `dm_conn.c` audit reaches the same conclusion independently.
It closes 57 linked functions / 6,216 code bytes and all action/interface
ingress. Fifty-six bodies have public r20.05 definitions, but the stock file
also contains the Ambiq 2.5 warning suppression, product validation/logger
paths, and one vendor-only helper. Five unused public APIs are dead-stripped.

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
4. **Resolved at the source-lineage level:** `app_db.c` is an AmbiqSuite
   application-framework descendant and stock expands it into a ten-record,
   role-aware MRAM database. The remaining `app_ble_peer_mgr.c` work is now a
   G2-local behavior/ABI reconstruction task, not an unidentified third-party
   dependency.

## Evidence commands (reproducible)

```
strings -a -t x <blob> | grep -iE 'cordio'          # source-path proof
# run = fileoff + 0x437FE0
# literal-pool xref: search image for little-endian <run addr> of each __FILE__
```

## Product WSF task root

The Cordio construction described above is now rooted in the product task TU
with retained path `platform\threads\thread_ble_wsf.c`. Its task entry at
`0x004D0A4C` calls the product `appBleStart` wrapper and then loops on
`WsfOsDispatcher` at `0x0052B9D0`. The static `ble_wsf` task uses stack
`0x20043A98` (16 KiB), CMSIS control block `0x20072140` (112 bytes), and
priority `0x31`.

The same TU owns the max-one transmit-ready semaphore that gates the product
BLE send paths and is released by thirteen completion sites. This is product
glue above Cordio: its retained path and binary behavior are exact, while its
source is not present in the public Ambiq/Packetcraft or authenticated local
SDK oracles. See `g2-thread-ble-wsf-recovery.md`.

## Product BLE message roots

The adjacent product message threads now close both sides of the WSF-facing
application transport. `thread_ble_msgtx.c` is bounded at
`[0x00475290,0x00475FC0)` with 21 bodies / 3,096 code bytes, while
`thread_ble_msgrx.c` is bounded at `[0x0048EDB0,0x0048F3A4)` with 13 bodies /
1,390 code bytes. Each uses a 150-entry pointer queue, a 16-KiB static stack,
and the same queue/exit flag bits; their lifecycle indices are 8 and 7.

These are product glue rather than Cordio source. The TX unit is already
clean-room replaced, while RX remains identified stock code. CMSIS-FreeRTOS
v10.5.1 qualifies the queue/thread provider ABI only. Exact bounds, protocol
dispatch, stored-entry closure, and ownership qualifications are in
`g2-thread-ble-message-recovery.md`.
