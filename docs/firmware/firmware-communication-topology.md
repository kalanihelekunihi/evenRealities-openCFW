# Firmware Communication Topology (G2-L, G2-R, G2-Case, R1-Ring)

Date: 2026-03-05  
Scope: which firmware file runs where, which runtime module owns it, and how components communicate with each other and with the user/app stack.

## 1. Topology Overview

```
Even.app (user UI)
  -> HTTPS API: /v2/g/login, /v2/g/check_latest_firmware
  -> CDN: cdn.evenreal.co/{firmware}
  -> BLE writes/notifies (G2: 0x5401/0x6401/0x7401; R1: BAE800xx, FE59)

G2-L / G2-R (Apollo510b main SoC + peripherals)
  -> internal bootloader/app handoff
  -> dispatch to display/touch/audio/ring/box services
  -> inter-eye sync link (TinyFrame over wired bridge)
  -> case relay (UART framing via box_uart_mgr)
  -> ring relay and/or direct ring control lane (service 0x91)

G2-Case MCU
  -> power/standby/task scheduler
  -> OTA bank swap path
  -> reports status to glasses over UART relay

R1-Ring (Nordic family)
  -> runtime BLE service BAE80001
  -> FE59 buttonless DFU + SMP/MCUmgr image upload
```

## 2. Firmware File -> Runtime Owner -> Link Map

| Firmware File | Device | Runtime Owner | Main Interface(s) | Key Downstream Links |
|---|---|---|---|---|
| `ota_s200_bootloader.bin` | G2-L/R | Apollo bootloader region | internal MRAM + VTOR/MSP jump | boots `ota_s200_firmware_ota.bin` |
| `ota_s200_firmware_ota.bin` | G2-L/R | Apollo main app | BLE (`0x5401/0x6401/0x7401`), RTOS threads | dispatches to display/touch/audio/ring/box subsystems |
| `firmware_ble_em9305.bin` | G2-L/R | EM9305 update service (`service_em9305_dfu`) | HCI record patch stream | BLE radio firmware/stack behavior |
| `firmware_touch.bin` | G2-L/R | touch DFU + gesture services | I2C DFU path | touch/wear/user-input triggers |
| `firmware_codec.bin` | G2-L/R | codec DFU/host services | TinyFrame serial/BINH stages | DMIC/I2S audio path |
| `firmware_box.bin` | G2-Case | case MCU runtime | UART relay through glasses | case battery/state/OTA |
| ring runtime image (separate package) | R1 | ring app + MCUboot | BAE800xx service, FE59/SMP DFU | ring gesture/health and firmware lifecycle |

## 2.1 G2 Boot-Owner Transition (`CONFIRMED`/`PARTIAL`)

```
ota_s200_bootloader.bin owner
  -> boot metadata + OTA decision
  -> handoff thunk: SCB->VTOR=0x00438000, MSP/BX to app vector

ota_s200_firmware_ota.bin owner
  -> reset entry 0x005C9776
     -> stack-limit + FPU/CPACR setup
     -> init-table walk (0x005C97F8)
     -> startup hub (0x005B4088)
        -> dynamic handoff: blx [0x20003DB4]
     -> runtime scheduler/thread bring-up (string-anchored)
```

Current boundary:
- Reset-to-hub chain is recovered with instruction-level anchors.
- Shared runtime object evidence exists for the same handoff base (`0x20003DB4`) via helper-path reads at `0x0048750C/0x00487520` (`[base+0x1c]`).
- Descriptor field semantics are now anchored through init-table emulation + runtime xrefs:
  - `+0x00`: startup callback pointer read (`blx [0x20003DB4]`) at `0x005B415E/0x005B4160`, confirmed value `0x00487423` (entry `0x00487422`)
  - `+0x04`: teardown callback seed `0x0048744B` (init-table materialized)
  - `+0x08`: worker handle field (`0x004873F4` store, `0x0048744C` read)
  - `+0x1C`: wait/sync field (`0x00486D94` store, `0x00486E92`/`0x004870AE`/`0x0048750C` reads)
- Worker-chain fan-out from this model is now anchored at `0x0048719C -> 0x00486E02 ->` descriptor list (`0x20003C60`, `0x20003D70`, `0x200034A0`, `0x20000614`, `0x20003DFC`, `0x20003D04`, `0x20003CBC`, `0x20003CE0`, `0x20003D28`, `0x20003DD8`, `0x20003D4C`).
- Init-table entry closure: startup table `0x00710830..0x00710878` materializes descriptor seed values before handoff; entry `0x00710858` LZ decode is the point where `[0x20003DB4]` becomes `0x00487423`.
- Post-dispatch runtime chain is now anchored: `0x00487422 -> 0x004873F4 -> 0x0048719C`, with stage2 wait/tick loop primitives (`os_event_wait_timeout=0x447A14`, `os_tick_now=0x447838`) matching idle/event-wait behavior.
- Stage2 idle loop is now instruction-closed: poll constant `0xEA60`, wait/tick calls (`0x48723A -> 0x447A34`, `0x487240 -> 0x447858`), and backedges (`0x48724C/0x487252/0x487256`) plus descriptor waiter gates (`0x486EA6`, `0x486EB8`, `[0x20003DB4+0x1C]`).
- OS-wrapper semantics are now mapped for startup/runtime gating and thread/event primitives (`os_ctx_guard`, `os_thread_create`, `os_thread_close`, `os_event_wait`, `os_event_wait_ex`), linking boot dispatch directly to steady-state wait behavior.
- Scheduler-core helpers behind wrappers are now lifted (`kernel_thread_create_*`, `kernel_thread_terminate`, `kernel_event_*`) with cross-domain xref samples (`0x0044xxxx`, `0x004Cxxxx`, `0x004Dxxxx`, `0x0051xxxx`), indicating runtime-wide usage.

## 3. G2 Internal Component Graph (Runtime)

```
thread_ble_msgrx / thread_ble_wsf
  -> *_common_data_handler (service-level)
     -> evenhub/display handlers
        -> display_thread -> displaydrv_manager -> drv_mspi_jbd4010 (MSPI)
     -> setting/gesture handlers
        -> service_gesture_processor / service_touch_dfu -> CY8C4046 (I2C)
     -> conversate/evenAI/audio handlers
        -> thread_audio -> codec host/dfu -> GX8002B (TinyFrame serial)
     -> ring handlers
        -> RingDataRelay_common_data_handler -> ring.proto/task.ring
     -> box handlers
        -> BoxDetect_common_data_handler -> box_uart_mgr (UART relay)
  -> response notify (0x5402 / 0x6402 / 0x7402)
```

Representative anchors (`ota_s200_firmware_ota.bin`):
- `thread_ble_msgrx` @ `3127436`
- `display_thread` @ `3133264`
- `Setting_common_data_handler` @ `3059448`
- `EvenAI_common_data_handler` @ `3036628`
- `RingDataRelay_common_data_handler` @ `2964504`
- `BoxDetect_common_data_handler` @ `3012536`
- `service_em9305_dfu.c` @ `2631853`
- `service_touch_dfu.c` @ `2632616`
- `drv_mspi_jbd4010.c` @ `2644620`

## 4. Device-to-Device Communication Paths

### 4.1 G2-L <-> G2-R

- Shared firmware image, runtime role split (`master`/`slave`).
- Inter-eye coordination uses TinyFrame sync paths (`SendInputEventToPeers`, `APP_PbTxEncodeScrollSync` anchors).
- Right-eye audio primacy remains capture-backed but role-ownership for ring routing is still mixed in local evidence.

### 4.2 G2 <-> Case

- Case has no direct BLE to phone.
- Glasses bridge case commands/status over UART (`box_uart_mgr`).
- Case boot chain is now anchored from reset to steady loop (`0x08000144 -> 0x080000B8 -> 0x08000270 -> 0x0800A3B0`, loop at `0x0800A4EE`).
- Scheduler/task bring-up is now anchored: `0x0800A4DE -> 0x08002F64 -> 0x0800A6F0 -> 0x0800678C -> 0x0800A718 -> 0x0800C09C`, with six thread-like and four queue/wait object entries recovered from `0x0800678C`.
- Case task-domain idle wait is now instruction-anchored in queue workers: calls into `0x08004EE8` with `wfi` at `0x08004EFE`, plus scheduler wait setup (`0x0800C0C2 -> 0x0800C81E`).
- G2-side case relay service chain is now instruction-anchored: dispatcher `0x004B4714` branches to notify/apply handlers (`0x004B44BE` / `0x004B4526`) and emits BLE response through `0x00463178` with `r0=0x81`.
- BoxDetect string/runtime closure is now corrected for wrapped-image addressing: handler xrefs target `0x00717798`, and case-sync message xref remains `0x004B4822 -> 0x007177B8`.
- OTA box flow is banked and CRC-guarded in `firmware_box.bin` (`[OTA_BOX]...`, `Swap bank...` markers).

### 4.3 G2 <-> R1 Ring

- Runtime ring lane uses G2 service `0x91` (`RingDataRelay_common_data_handler`).
- Service descriptor binding is now executable-anchored: `0x0067643C=0x91`, handler pointer `0x00676440=0x005B46B1`.
- Ring relay call chain is instruction-closed: `0x005B46B0 -> 0x005B41FC` and outbound send `0x005B46A4 -> 0x0046F5C4` with `r1=0x91`.
- Ring also exposes direct BLE service `BAE80001-...`.
- Ring DFU trigger via `FE59`, then SMP upload.
- Bundled Nordic binaries now have confirmed startup-to-idle anchors: bootloader reset/stage1/stage2 path (`0x000F83D8 -> 0x000F8200 -> 0x000FADC8/0x000FADBC`), init-walker backedge (`0x000F84DE -> 0x000F84CE`), SoftDevice pre-reset `wfe` loop (`0x00025FDC <-> 0x00025FDE`), and reset dispatch (`0x00025FE0 -> 0x00001108`), while standalone ring app runtime remains out-of-corpus.

### 4.4 G2 System-Monitor Lane

- System-monitor service binding is now executable-anchored: `0x006764EC=0xFF`, handler pointer `0x006764F0=0x005221D5`.
- Monitor notify sender `0x00522184` is caller-linked from runtime control path (`0x004D0972`) and sends via `0x005221CC -> 0x00463178` with `r0=0xFF`.
- Handler lane `0x005221D4` is string-xref anchored (`system_monitor_common_data_handler`) and loads idle command marker at `0x005223A8 -> 0x006A1EB4`.

## 5. User/API -> BLE -> Firmware Path

### 5.1 Runtime User Action

```
User action in Even.app
  -> app encodes protobuf/event packet
  -> BLE write (0x5401 or 0x6401)
  -> G2 handler executes + optional component callout
  -> BLE notify response (0x5402 or 0x6402)
  -> app updates UI state
```

### 5.2 Firmware Update Lifecycle

```
POST /v2/g/login
  -> JWT token
GET /v2/g/check_latest_firmware
  -> version + subPath + fileSign
GET https://cdn.evenreal.co{subPath}
  -> EVENOTA package
BLE file channel: FILE_CHECK -> START -> DATA -> END (0x7401/0x7402)
  -> staged in glasses
bootloader install + reboot
  -> app runtime starts, then subcomponent updates if needed
```

Current contract note:
- `check_latest_firmware` is the stable successful retrieval route in local evidence.
- `check_firmware` remains unresolved (`1401 Params error`).

## 6. Evidence Pointers

- Boot/call trees: `docs/firmware/device-boot-call-trees.md`
- Firmware/API flow: `docs/firmware/firmware-updates.md`
- OTA wire protocol: `docs/firmware/ota-protocol.md`
- File/component map: `docs/firmware/firmware-files.md`
- Hardware boundary evidence: `captures/firmware/analysis/2026-03-03-hardware-functionality-mapping.json`
- BLE UUID/service evidence: `captures/firmware/analysis/2026-03-03-ble-artifact-extraction.json`
- Startup callgraph evidence: `captures/firmware/analysis/2026-03-05-g2-reset-startup-callgraph.md`
- Startup disassembly notes: `captures/firmware/analysis/2026-03-05-g2-reset-startup-disassembly-notes.md`
- Dispatch descriptor chain: `captures/firmware/analysis/2026-03-05-g2-dispatch-descriptor-chain.md`
- Startup init-table effects (confirmed callback): `captures/firmware/analysis/2026-03-05-g2-startup-init-table-effects.md`
- Runtime entry-chain closure: `captures/firmware/analysis/2026-03-05-g2-runtime-entry-chain.md`
- OS-wrapper semantic map: `captures/firmware/analysis/2026-03-05-g2-os-wrapper-semantics.md`
- Scheduler-core semantic map: `captures/firmware/analysis/2026-03-05-g2-scheduler-core-semantics.md`
- G2 idle/wait loop closure: `captures/firmware/analysis/2026-03-05-g2-idle-wait-calltree.md`
- G2 BoxDetect BLE/user chain closure: `captures/firmware/analysis/2026-03-05-g2-boxdetect-ble-chain.md`
- G2 ring relay executable chain: `captures/firmware/analysis/2026-03-05-g2-ring-relay-callchain.md`
- G2 system-monitor executable chain: `captures/firmware/analysis/2026-03-05-g2-system-monitor-callchain.md`
- Case reset/startup callgraph: `captures/firmware/analysis/2026-03-05-box-reset-startup-callgraph.md`
- Case scheduler/task map: `captures/firmware/analysis/2026-03-05-box-scheduler-task-map.md`
- R1 Nordic DFU startup chains: `captures/firmware/analysis/2026-03-05-r1-nordic-dfu-startup-chain.md`
- R1 Nordic stage2/idle paths: `captures/firmware/analysis/2026-03-05-r1-nordic-stage2-idle-paths.md`
- Root callback candidate (superseded by confirmed init-table proof): `captures/firmware/analysis/2026-03-05-g2-dispatch-root-callback-candidate.md`
