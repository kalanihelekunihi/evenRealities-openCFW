# Service Dispatch Architecture

> Analysis performed 2026-03-05. Firmware: `captures/firmware/g2_extracted/ota_s200_firmware_ota.bin`.

---

## 1. Root Dispatcher Callback

Confidence: `LIKELY` (upgraded to confirmed via init-table emulation)

### Startup Call Site

- startup load site: `0x005B415C` -> deref `0x20003DB4` then indirect call

```asm
0x005B415C: ldr      r0, [pc, #0x98]
0x005B415E: ldr      r0, [r0]
0x005B4160: blx      r0
0x005B4162: b        #0x5b4162
```

### Candidate Value

- candidate callback pointer: `0x00487423`
- word-occurrence count in image: `1`
- occurrence addresses: `0x00742798`

### Candidate Function Window

```asm
0x00487422: push     {r7, lr}
0x00487424: bl       #0x4477d0
0x00487428: movs     r2, #0
0x0048742A: movs     r1, #0
0x0048742C: ldr      r0, [pc, #0x1d4]
0x0048742E: bl       #0x44784e
0x00487432: cmp      r0, #0
0x00487434: bne      #0x487444
0x00487436: bl       #0x5d6cdc
0x0048743A: movs     r0, #0
0x0048743C: movs.w   r1, #-1
0x00487440: str      r0, [r1]
0x00487442: b        #0x487442
0x00487444: bl       #0x447800
0x00487448: pop      {r0, pc}
0x0048744A: push     {r4, lr}
0x0048744C: ldr      r4, [pc, #0xe0]
0x0048744E: ldr      r0, [r4, #8]
0x00487450: cmp      r0, #0
0x00487452: beq      #0x48745e
```

### Worker Function Window

```asm
0x004873F4: push     {r4, lr}
0x004873F6: ldr      r4, [pc, #0x138]
0x004873F8: ldr      r2, [pc, #0x200]
0x004873FA: movs     r1, #0
0x004873FC: ldr      r0, [pc, #0x200]
0x004873FE: bl       #0x44784e
0x00487402: str      r0, [r4, #8]
0x00487404: ldr      r0, [r4, #8]
0x00487406: cmp      r0, #0
0x00487408: bne      #0x487418
0x0048740A: bl       #0x5d6cdc
0x0048740E: movs     r0, #0
0x00487410: movs.w   r1, #-1
0x00487414: str      r0, [r1]
0x00487416: b        #0x487416
0x00487418: bl       #0x447916
0x0048741C: bl       #0x447950
0x00487420: pop      {r4, pc}
0x00487422: push     {r7, lr}
0x00487424: bl       #0x4477d0
0x00487428: movs     r2, #0
0x0048742A: movs     r1, #0
0x0048742C: ldr      r0, [pc, #0x1d4]
0x0048742E: bl       #0x44784e
```

### Interpretation

- Startup dispatch through `[0x20003DB4 + 0x00]` is confirmed, but direct initializer proof is still open.
- `0x00487423` remains the strongest candidate because its function window creates worker entry `0x004873F5`, which in turn initializes descriptor-linked runtime state (`+0x08` handle path).

---

## 2. Descriptor Chain Walk

### Image Metadata

- `run_base`: `0x00438000`
- `vector_reset`: `0x005C9777`
- `target_descriptor`: `0x20003DB4`

### Descriptor Xrefs

- xref count: `8`
- observed field offsets: `0x0, 0x8, 0x1c`

| Load Site | Next Accesses |
|---:|---|
| `0x00486D96` | `str r0, [r4, #0x1c]` @ `0x00486DA0` (disp `28`), `ldr r0, [r4, #0x1c]` @ `0x00486DA2` (disp `28`) |
| `0x00486E92` | `ldr r0, [r0, #0x1c]` @ `0x00486E96` (disp `28`) |
| `0x004870AE` | `ldr r0, [r0, #0x1c]` @ `0x004870B2` (disp `28`) |
| `0x004873F6` | `str r0, [r4, #8]` @ `0x00487402` (disp `8`) |
| `0x0048744C` | `ldr r0, [r4, #8]` @ `0x0048744E` (disp `8`), `ldr r0, [r4, #8]` @ `0x00487454` (disp `8`) |
| `0x0048750C` | `ldr r0, [r0, #0x1c]` @ `0x0048750E` (disp `28`) |
| `0x00487520` | `ldr r0, [r0, #0x1c]` @ `0x00487522` (disp `28`) |
| `0x005B415C` | `ldr r0, [r0]` @ `0x005B415E` (disp `0`) |

### Startup Bridge

- startup handoff site: `0x005B415C` -> `ldr r0, [0x20003DB4]` then `blx r0` at `0x005B4160`

### Sub-Descriptor Fan-Out Literals

- literal table base: `0x00487548`
- slot `0`: `0x20003C60`
- slot `1`: `0x20003D70`
- slot `2`: `0x200034A0`
- slot `3`: `0x20000614`
- slot `4`: `0x20003DFC`
- slot `5`: `0x20003D04`
- slot `6`: `0x20003CBC`
- slot `7`: `0x20003CE0`
- slot `8`: `0x20003D28`
- slot `9`: `0x20003DD8`
- slot `10`: `0x20003D4C`

### Call-Chain Hints

- function `0x0048719C` calls:
  - `0x004871A0` -> `0x00486D94` (`bl`)
  - `0x004871A4` -> `0x00486DD0` (`bl`)
  - `0x004871A8` -> `0x00486DE4` (`bl`)
  - `0x004871AC` -> `0x00486EF8` (`bl`)
  - `0x004871B8` -> `0x0043CD6C` (`bl`)
  - `0x004871E0` -> `0x0043D1C8` (`bl`)
  - `0x004871E4` -> `0x0043CD6C` (`bl`)
  - `0x004871EC` -> `0x0043CD6C` (`bl`)
  - `0x00487202` -> `0x0043CCC8` (`bl`)
  - `0x0048720A` -> `0x00487238` (`bl`)
  - `0x0048721A` -> `0x00447A14` (`bl`)
  - `0x00487220` -> `0x00447838` (`bl`)
  - `0x00487240` -> `0x0043CD6C` (`bl`)
  - `0x00487262` -> `0x0043D1C8` (`bl`)
  - `0x00487266` -> `0x0043CD6C` (`bl`)
  - `0x0048726E` -> `0x0043CD6C` (`bl`)
  - `0x00487280` -> `0x0043CCC8` (`bl`)
  - `0x00487294` -> `0x00487054` (`bl`)
  - `0x0048729C` -> `0x0043CD6C` (`bl`)
  - `0x004872BA` -> `0x0043D1C8` (`bl`)
  - `0x004872BE` -> `0x0043CD6C` (`bl`)
  - `0x004872C6` -> `0x0043CD6C` (`bl`)
  - `0x004872D8` -> `0x0043CCC8` (`bl`)
  - `0x004872DE` -> `0x00487054` (`bl`)
  - `0x004872E6` -> `0x0043CD6C` (`bl`)
- function `0x004873F4` calls:
  - `0x004873FE` -> `0x0044784E` (`bl`)
  - `0x0048740A` -> `0x005D6CDC` (`bl`)
  - `0x00487418` -> `0x00447916` (`bl`)
  - `0x0048741C` -> `0x00447950` (`bl`)
- function `0x00486D94` calls:
  - `0x00486D9C` -> `0x00447CE2` (`bl`)
  - `0x00486DA8` -> `0x005D6CDC` (`bl`)
  - `0x00486DCA` -> `0x0049A3F0` (`bl`)
- function `0x00486E02` calls:
  - `0x00486E04` -> `0x00447916` (`bl`)
  - `0x00486E0A` -> `0x0044791E` (`bl`)
  - `0x00486E0E` -> `0x004D0770` (`bl`)
  - `0x00486E12` -> `0x004D0A6C` (`bl`)
  - `0x00486E6E` -> `0x00447916` (`bl`)
  - `0x00486E74` -> `0x0044791E` (`bl`)

---

## 3. Per-Service Handler Callchains

### 3.1 System Monitor (0xFF)

#### Descriptor Binding

- service word `0x006764EC` = `0x000000FF`
- handler pointer word `0x006764F0` = `0x005221D5`
- pointer matches handler entry (`+1` thumb): `True`

#### Key Functions

- monitor notify sender: `0x00522184`
- monitor handler: `0x005221D4`
- BLE send wrapper: `0x00463178`

#### Bridge and BLE Lane Closure

- caller `0x004D0972` -> notify sender `0x00522184`
- notify sender -> BLE: `0x005221CC -> 0x00463178` with `r0=0xFF` and immediates `{'r0': '0x000000FF', 'r1': '0x00000078', 'r2': '0x00000006', 'r3': '0x00000000'}`

#### String Anchors In Executable Ranges

- `system_monitor_common_data_handler` runtime `0x0070E574`
  - xref `0x005221F0` (ldr r3, [pc, #0x1d8])
  - xref `0x00522262` (ldr r3, [pc, #0x168])
  - xref `0x005222A2` (ldr r3, [pc, #0x128])
  - xref `0x005222E2` (ldr r3, [pc, #0xe8])
  - xref `0x0052232C` (ldr r3, [pc, #0x9c])
  - xref `0x0052238C` (ldr r3, [pc, #0x3c])
- idle command marker runtime `0x006A1EB4`
  - xref `0x005223A8` (ldr r1, [pc, #0x54])

#### Interpretation

- Service table binds `0xFF` to handler `0x005221D4` (`0x005221D5` stored as thumb pointer).
- Monitor notify function `0x00522184` sends a fixed probe frame through `0x00463178` with `r0=0xFF`.
- Handler body is string-anchored to `system_monitor_common_data_handler` and the idle-command message, closing the monitor-to-scheduler idle handoff path.

### 3.2 Ring Relay (0x91)

#### Descriptor Binding

- service word `0x0067643C` = `0x00000091`
- handler pointer word `0x00676440` = `0x005B46B1`
- pointer matches wrapper entry (`+1` thumb): `True`

#### Key Functions

- wrapper entry: `0x005B46B0`
- frame parser: `0x005B41FC`
- build/send path: `0x005B4506`
- ring send wrapper: `0x0046F5C4`

#### String Anchors In Executable Ranges

- `RingDataRelay_common_data_handler` runtime `0x0070BBF8`
  - xref `0x005B46CE` (ldr r3, [pc, #0x104])
  - xref `0x005B471E` (ldr r3, [pc, #0xb4])
- `APP_PbRxRingFrameDataProcess` runtime `0x007167B8`
  - xref `0x005B421E` (ldr.w r3, [pc, #0x534])
  - xref `0x005B4268` (ldr.w r3, [pc, #0x4e8])
  - xref `0x005B42F6` (ldr.w r3, [pc, #0x45c])
  - xref `0x005B434E` (ldr.w r3, [pc, #0x404])
  - xref `0x005B43B6` (ldr.w r3, [pc, #0x39c])
- parser diagnostic strings: `ring command_id`, `unknown command_id`, `unknown event_id`, `unknown event type`
  - `[pb.ring]ring command_id: %d`:
    - `0x005B4370` (ldr.w r1, [pc, #0x410])
  - `[pb.ring]Unknown command_id: %d`:
    - `0x005B43D8` (ldr.w r1, [pc, #0x3b0])
  - `[pb.ring]Unknown event_id: %d`:
    - `0x005B44F0` (ldr.w r1, [pc, #0x2b8])
  - `[pb.ring]Unknown event type: %d`:
    - `0x005B473A` (ldr r1, [pc, #0xa4])

#### Call-Chain Evidence

- wrapper -> parser: `0x005B4704 -> 0x005B41FC`
- build/send -> ring wrapper: `0x005B46A4 -> 0x0046F5C4` with `r1=0x91` and immediates `{'r0': '0x00000001', 'r1': '0x00000091'}`

#### Interpretation

- Service table binds service `0x91` directly to wrapper `0x005B46B0` (`0x005B46B1` stored as thumb pointer).
- Wrapper invokes parser `0x005B41FC`, which contains `APP_PbRxRingFrameDataProcess` + ring command/event diagnostic string xrefs.
- Parser/build path emits outbound relay frames through `0x0046F5C4` with immediate service selector `r1=0x91`, closing the user/BLE ring relay lane.

### 3.3 Navigation / DeviceInfo Descriptor-Adjacent Lanes

This artifact captures executable anchors adjacent to the unresolved `0x08` and `0x09` service descriptor slots.
The descriptor-table encoding is still not fully decoded, so this report stays at the level of adjacent code-entry recovery and string/call correlation.

#### Service 0x08 (Navigation)

- service word `0x0067641C` = `0x00000008`
- primary entry word `0x00676420` = `0x00588817`
- secondary entry word `0x00676424` = `0x00588AF3`
- shared context word `0x00676428` = `0x20002BE4`

##### Primary Lane

- descriptor entry `0x00676420` -> thumb pointer `0x00588817`
- first substantial prologue `0x0058882C` through `0x00588AA8`
- string-backed evidence:
  - `0x0058886E` -> `0x006CCF80` = `D:\01_workspace\s200_ap510b_iar\app\gui\navigation\navigation.c`
  - `0x005888D4` -> `0x006CCF80` = `D:\01_workspace\s200_ap510b_iar\app\gui\navigation\navigation.c`
  - `0x00588998` -> `0x006CCF80` = `D:\01_workspace\s200_ap510b_iar\app\gui\navigation\navigation.c`
  - `0x005889F6` -> `0x006CCF80` = `D:\01_workspace\s200_ap510b_iar\app\gui\navigation\navigation.c`
  - `0x00588A54` -> `0x006CCF80` = `D:\01_workspace\s200_ap510b_iar\app\gui\navigation\navigation.c`
- call anchors:
  - `0x00588922 -> 0x00583230` (`navigation_lane_primary_worker`)
  - `0x0058893E -> 0x00583230` (`navigation_lane_primary_worker`)
  - `0x0058895A -> 0x00583230` (`navigation_lane_primary_worker`)
  - `0x00588976 -> 0x00583230` (`navigation_lane_primary_worker`)
  - `0x005889D4 -> 0x00583230` (`navigation_lane_primary_worker`)
  - `0x00588A32 -> 0x00583230` (`navigation_lane_primary_worker`)
  - `0x00588A90 -> 0x00583230` (`navigation_lane_primary_worker`)

##### Secondary Lane

- descriptor entry `0x00676424` -> thumb pointer `0x00588AF3`
- first substantial prologue `0x00588AF2` through `0x00588D20`
- string-backed evidence:
  - `0x00588B12` -> `0x006CCF80` = `D:\01_workspace\s200_ap510b_iar\app\gui\navigation\navigation.c`
- call anchors:
  - `0x00588B4A -> 0x00580018` (`navigation_lane_secondary_worker`)
  - `0x00588B58 -> 0x004B3F66` (`navigation_display_commit`)
  - `0x00588B6A -> 0x00583B9C` (`navigation_lane_secondary_transition`)
- shared-context writes:
  - context literal `0x00588B52` followed by store `0x00588B54` (`r1, [r2, #4]`)

##### Interpretation

- Descriptor-adjacent 0x08 code carries navigation-specific string literals and writes back through the shared context slot.
- Entry pointers land in small wrapper fragments; first substantial prologues are later in the same code island.

#### Service 0x09 (DeviceInfo/DevConfig Bridge)

- service word `0x006764BC` = `0x00000009`
- primary entry word `0x006764C0` = `0x00464481`
- secondary entry word `0x006764C4` = `0x00465209`
- shared context word `0x006764C8` = `0x20003848`

##### Primary Lane

- descriptor entry `0x006764C0` -> thumb pointer `0x00464481`
- first substantial prologue `0x00464480` through `0x00464548`
- string-backed evidence:
  - `0x0046449A` -> `0x00722EF4` = `BLE data parsing started`
  - `0x004644C6` -> `0x0070DE00` = `[setting]BLE data parsing started`
- call anchors:
  - `0x004644DE -> 0x004AA30C` (`settings_parser_bridge`)
  - `0x00464540 -> 0x004676E6` (`devinfo_query_fallback`)

##### Secondary Lane

- descriptor entry `0x006764C4` -> thumb pointer `0x00465209`
- first substantial prologue `0x00465208` through `0x004652A2`
- call anchors:
  - `0x0046525A -> 0x004AF286` (`dominant_hand_reader`)
  - `0x0046526A -> 0x004AF4F8` (`head_up_calibration_gate`)
  - `0x0046526E -> 0x00467254` (`settings_status_context`)
  - `0x00465276 -> 0x004AAEE4` (`settings_status_notify_wrapper`)
  - `0x00465282 -> 0x00467254` (`settings_status_context`)
  - `0x00465292 -> 0x004AAF94` (`settings_notify_wrapper_case5`)
  - `0x00465296 -> 0x004AAEE4` (`settings_status_notify_wrapper`)
- shared-context writes:
  - context literal `0x00465262` followed by store `0x00465264` (`r0, [r1, #4]`)

##### Interpretation

- Descriptor-adjacent 0x09 code reuses the shared settings/dev-config parser path rather than behaving like a pure read-only info lane.
- Secondary code writes shared context state at `ctx+0x04` and toggles calibration/status wrappers already anchored in the 0x0D settings artifacts.

### 3.4 BoxDetect / BLE Chain (0x81)

#### Key Functions

- dispatcher: `0x004B4714`
- notify pack/sender: `0x004B44BE`
- state/apply path: `0x004B4526`
- BLE send wrapper: `0x00463178`
- auxiliary callee candidate: `0x00543E06`

#### Handler/Parser String Xrefs

- `BoxDetect_common_data_handler` string: `0x00717798`
  - xref `0x004B4754` (ldr r3, [pc, #0x1c4])
  - xref `0x004B47A8` (ldr r3, [pc, #0x170])
  - xref `0x004B47EA` (ldr r3, [pc, #0x130])
  - xref `0x004B482C` (ldr r3, [pc, #0xec])
  - xref `0x004B4872` (ldr r3, [pc, #0xa8])
- `Received case sync notification` string: `0x007177B8`
  - xref `0x004B4822` (ldr r0, [pc, #0x110])

#### Dispatch Cases (r0 command selector)

- `0x004B471C` compares `r0` with `0x00`
  - `0x004B471E` bne -> `0x004B4730`
- `0x004B4730` compares `r0` with `0x05`
  - `0x004B4738` beq -> `0x004B473E`
  - `0x004B473C` bhs -> `0x004B4786`
- `0x004B4788` compares `r0` with `0x01`
  - `0x004B478A` beq -> `0x004B4796`
  - `0x004B478C` blo -> `0x004B485C`
  - `0x004B4790` beq -> `0x004B481A`
- `0x004B478E` compares `r0` with `0x03`
  - `0x004B4790` beq -> `0x004B481A`
  - `0x004B4792` blo -> `0x004B47D8`
  - `0x004B4794` b -> `0x004B485C`

- dispatch callsites to state/apply path:
  - `0x004B4814 -> 0x004B4526`
  - `0x004B4856 -> 0x004B4526`
- dispatch callsites to notify path:
  - `0x004B47D2 -> 0x004B44BE`

- direct calls from dispatcher:
  - `0x004B4726 -> 0x004FC728`
  - `0x004B473E -> 0x0043CD6C`
  - `0x004B475C -> 0x0043D1C8`
  - `0x004B4760 -> 0x0043CD6C`
  - `0x004B4768 -> 0x0043CD6C`
  - `0x004B477C -> 0x0043CCC8`
  - `0x004B4796 -> 0x0043CD6C`
  - `0x004B47B0 -> 0x0043D1C8`
  - `0x004B47B4 -> 0x0043CD6C`
  - `0x004B47BC -> 0x0043CD6C`
  - `0x004B47CC -> 0x0043CCC8`
  - `0x004B47D2 -> 0x004B44BE`
  - `0x004B47D8 -> 0x0043CD6C`
  - `0x004B47F2 -> 0x0043D1C8`
  - `0x004B47F6 -> 0x0043CD6C`
  - `0x004B47FE -> 0x0043CD6C`
  - `0x004B480E -> 0x0043CCC8`
  - `0x004B4814 -> 0x004B4526`

#### BLE Notify Lane Evidence

- `0x004B451E -> 0x00463178` with `r0=0x81` and args `{'r0': '0x00000081', 'r2': '0x00000008', 'r3': '0x00000000'}`

#### Auxiliary Callee Bridge

- caller `0x00545866` -> parser `0x00543E06`

#### Interpretation

- BoxDetect command dispatch is concretely separated into status/notify and state-apply paths, then returns to the 0x81 response lane.
- The notify builder calls BLE send wrapper with service id `0x81`, closing a concrete case-status-to-user notify path.
- `Received case sync notification` remains dispatch-anchored in BoxDetect (`0x004B4822`), while auxiliary callee `0x00543E06` is preserved as a caller-linked edge pending deeper semantic lift.
