# Device Boot Process and Runtime Call Trees (G2-L, G2-R, G2-Case, R1-Ring)

Date: 2026-03-05  
Scope: boot-to-app-start call trees, idle/wait state paths, component boundaries, and user/API/BLE communication paths.

## 1. Evidence Scope and Confidence

- `CONFIRMED`: direct binary/vector/string evidence in local firmware artifacts.
- `LIKELY`: strong string/path evidence but missing full symbolized call graph.
- `INFERRED`: behavior modeled from app/DFU frameworks and protocol traces where device firmware image is not present locally.

Primary artifacts used:
- `captures/firmware/g2_extracted/*`
- `captures/firmware/analysis/2026-03-03-g2-extracted-wave.md`
- `captures/firmware/analysis/2026-03-03-hardware-functionality-mapping.md`
- `captures/firmware/analysis/2026-03-03-ble-artifact-extraction.md`
- `captures/firmware/analysis/2026-03-05-g2-reset-startup-callgraph.md`
- `captures/firmware/analysis/2026-03-05-g2-reset-startup-disassembly-notes.md`
- `captures/firmware/analysis/2026-03-05-g2-dispatch-descriptor-chain.md`
- `captures/firmware/analysis/2026-03-05-g2-dispatch-root-callback-candidate.md`
- `captures/firmware/analysis/2026-03-05-g2-startup-init-table-effects.md`
- `captures/firmware/analysis/2026-03-05-g2-runtime-entry-chain.md`
- `captures/firmware/analysis/2026-03-05-g2-os-wrapper-semantics.md`
- `captures/firmware/analysis/2026-03-05-g2-scheduler-core-semantics.md`
- `captures/firmware/analysis/2026-03-05-g2-idle-wait-calltree.md`
- `captures/firmware/analysis/2026-03-05-g2-boxdetect-ble-chain.md`
- `captures/firmware/analysis/2026-03-05-g2-ring-relay-callchain.md`
- `captures/firmware/analysis/2026-03-05-g2-system-monitor-callchain.md`
- `captures/firmware/analysis/2026-03-05-box-reset-startup-callgraph.md`
- `captures/firmware/analysis/2026-03-05-box-scheduler-task-map.md`
- `captures/firmware/analysis/2026-03-05-r1-nordic-dfu-startup-chain.md`
- `captures/firmware/analysis/2026-03-05-r1-nordic-stage2-idle-paths.md`
- `captures/20260301-2-testAll.txt`
- `captures/20260302-2-testAll.txt`
- `captures/20260302-3-testAll.txt`
- `captures/firmware/B210_BL_DFU_NO_v2.0.3.0004/bootloader.bin`
- `captures/firmware/B210_ALWAY_BL_DFU_NO/bootloader.bin`
- `captures/firmware/B210_SD_ONLY_NO_v2.0.3.0004/softdevice.bin`
- `docs/firmware/{s200-bootloader.md,s200-firmware-ota.md,box-case-mcu.md,firmware-files.md,firmware-updates.md}`
- `docs/firmware/g2-firmware-modules.md`
- `docs/devices/{g2-glasses.md,g2-case.md,r1-ring.md}`

## 2. Firmware Artifacts by Device

| Device | Boot/Runtime Firmware Files | Notes |
|---|---|---|
| G2-L | `ota_s200_bootloader.bin`, `ota_s200_firmware_ota.bin`, `firmware_ble_em9305.bin`, `firmware_touch.bin`, `firmware_codec.bin` | Same binaries as G2-R; role selected at runtime (`_L` name/role state). |
| G2-R | `ota_s200_bootloader.bin`, `ota_s200_firmware_ota.bin`, `firmware_ble_em9305.bin`, `firmware_touch.bin`, `firmware_codec.bin` | Same binaries as G2-L; role selected at runtime (`_R` name/role state). |
| G2-Case | `firmware_box.bin` | Updated through glasses relay (no direct BLE to phone). |
| R1-Ring | Not in EVENOTA package | Uses separate Nordic DFU/SMP pipeline (`FE59` + MCUmgr). |

## 3. G2-L / G2-R Boot and Call Trees

### 3.1 Common Boot Chain (`CONFIRMED`)

```
Power-on / reset
  -> Bootloader vector @ 0x00410000
     SP=0x2007FB00, Reset=0x004324CF
  -> bootloader main path
     -> thread_manager_sysstart_sync / task.manager startup sync
     -> littlefs_init + /firmware /ota /user /log mount paths
     -> otaFlag check + is_need_updata_image
        -> if OTA pending:
           app_dfu_image_crc_check
           app_dfu_system_program
           _verifyFlashContent
        -> else: handoff to app
     -> VTOR handoff thunk (0x0042DBDC):
        SCB->VTOR = 0x00438000
        MSP = *(0x00438000)
        BX *(0x00438004)
  -> Main app vector @ 0x00438000
     SP=0x2007FB00, Reset=0x005C9777
```

Anchors:
- Bootloader handoff proof (`str r0, [0xE000ED08]`, `ldr sp, [r0]`, `bx r1`) in `2026-03-03-g2-extracted-wave.md`.
- Bootloader strings: `bootMetadataInfo.targetRunAddr`, `APP jumpaddr app(...)`, `DO NOT need updata firmware, GO TO APP`.

### 3.2 Main App Startup to Idle/Event Wait (`PARTIAL`: reset-path disassembly recovered + runtime anchors)

#### 3.2.1 Reset-Vector Startup Chain (`CONFIRMED`)

```
Reset entry (0x005C9776; vector reset 0x005C9777)
  -> set stack limits:
     MSPLIM = 0x2007D000
     PSPLIM = 0x2007D000
  -> call 0x005C9798
     -> call 0x005C97B4
        -> CPACR/FPU enable sequence (E000ED88, OR 0x00F00000, DSB/ISB)
     -> call 0x005C97D8
        -> call 0x005C976C
           -> SCB->VTOR = 0x00438000 (main app vector base)
        -> call 0x005C97F8
           -> bounded init-function loop (`blx` through table entries)
        -> call 0x005B4088
           -> platform/bootstrap hub:
              0x004A8BB6, 0x005A41F0, 0x005B3DE0, 0x00468D9E, ...
           -> dynamic runtime handoff: `blx [0x20003DB4]`
        -> call 0x005C9820
           -> non-returning loop calling 0x0053AC08
```

Anchors:
- `captures/firmware/analysis/2026-03-05-g2-reset-startup-callgraph.md`
- `captures/firmware/analysis/2026-03-05-g2-reset-startup-callgraph.json`
- `captures/firmware/analysis/2026-03-05-g2-reset-startup-disassembly-notes.md`

Dynamic handoff boundary note:
- `0x20003DB4` is also referenced by runtime helper paths (`0x0048750C`, `0x00487520`) via `[base+0x1c]`, supporting the current model that this RAM object is a shared startup/runtime dispatch/control structure.

#### 3.2.2 Runtime Bring-Up to Idle/Event Wait (`PARTIAL` with confirmed dispatch entry)

The static reset path above is now confirmed through the early startup handoff. Init-table emulation now confirms the dynamic callback value (`[0x20003DB4] = 0x00487423`), so the runtime entry function (`0x00487422`) is known; thread/service naming below remains partially string-anchor-based deeper in the chain.

```
0x005B415C: ldr r0, [0x20003DB4] -> 0x00487423
0x005B4160: blx r0                -> 0x00487422
0x00487422: bootstrap worker via os_thread_create (0x44784E, entry=0x004873F5)
0x004873F4: seeds [0x20003DB4 + 0x08] runtime worker handle
```

```
RAM-dispatched runtime entry (after 0x005B4088)
  -> product/s200 app config init (main.c path anchor)
  -> resource/queue init
     -> fw_evt_loop init
     -> sensor_hub queue init
     -> device_mgr queue init
     -> display driver queue/thread init
  -> BLE/profile init
     -> APP_BleEusHandlerInit (control)
     -> APP_BleEfsHandlerInit (file)
     -> APP_BleNusHandlerInit (NUS)
     -> APP_BleRingHandlerInit (ring bridge profile)
  -> worker/thread bring-up
     -> thread_ble_msgrx
     -> thread_ble_msgtx
     -> thread_ble_wsf
     -> thread_input
     -> thread_audio
     -> thread_ring
     -> thread_notification
     -> thread_evenai
     -> display_thread
     -> thread_pool workers
  -> scheduler steady state
     -> wait on BLE queues/semaphores/events
     -> wait on input/touch/ring/sensor events
     -> emit async responses + display updates
```

Idle/wait markers:
- `fw_evt_loop_thread_id is NULL` wait messages.
- `[task.ble.wsf]wait_tx_ready success...`.
- Queue/overflow guards: `ESS queue full`, queue-clear logs.
- System monitor idle path: `send idle command to schedule manager`.

#### 3.2.3 RAM Dispatch Descriptor Chain (`CONFIRMED` for boot seed + `PARTIAL` for full symbolization)

`0x20003DB4` is now resolved as a startup/runtime dispatch descriptor object with boot-seed values recovered from init-table emulation.

```
startup hub (0x005B4088)
  -> ldr r0, [0x20003DB4] ; descriptor field +0x00
  -> blx r0               ; dynamic startup callback

init-table seed state (emulated from 0x005C97F8 entries)
  -> [0x20003DB4 + 0x00] = 0x00487423 (entry 0x00487422)
  -> [0x20003DB4 + 0x04] = 0x0048744B
  -> [0x20003DB4 + 0x08] = 0x00000000 (later runtime-populated)
  -> [0x20003DB4 + 0x1C] = 0x00000000 (later runtime-populated)

descriptor-linked runtime helpers
  -> 0x00486D94:
     [0x20003DB4 + 0x1C] = 0x447CE2(...)
  -> 0x004873F4:
     [0x20003DB4 + 0x08] = 0x44784E(entry=0x0048719D, ...)
  -> 0x0048744C / 0x00486E92 / 0x004870AE / 0x0048750C / 0x00487520:
     wait/poll/read paths using descriptor fields +0x08 and +0x1C

worker entry path
  -> 0x0048719C
     -> calls 0x00486D94, 0x00486DD0, 0x00486DE4, 0x00486EF8
     -> enters periodic wait loop (os_event_wait_timeout `0x447A14` / os_tick_now `0x447838`)
```

Sub-descriptor fan-out recovered from literal table (`0x00487548`), used by `0x00486E02`:
- `0x20003C60`
- `0x20003D70`
- `0x200034A0`
- `0x20000614`
- `0x20003DFC`
- `0x20003D04`
- `0x20003CBC`
- `0x20003CE0`
- `0x20003D28`
- `0x20003DD8`
- `0x20003D4C`

Interpretation: startup enters a descriptor-driven bootstrap model where `0x20003DB4` acts as a top-level dispatch/control object and `0x00486E02` fans out into additional descriptor callbacks.

Root callback resolution (`CONFIRMED`):
- Init-table emulation shows entry `0x00710858` (LZ handler `0x0043A11F`) materializes `[0x20003DB4 + 0x00] = 0x00487423` before startup handoff.
- `0x00487423` (entry `0x00487422`) creates worker entry `0x004873F5`, which aligns with descriptor-linked runtime setup (`+0x08`/`+0x1C` paths).
- Confirmation artifact: `captures/firmware/analysis/2026-03-05-g2-startup-init-table-effects.md`.

#### 3.2.4 Post-Dispatch Runtime Chain (`CONFIRMED`/`PARTIAL`)

Recovered bootstrap sequence after `blx [0x20003DB4]`:

```
0x00487422 (dispatch-entry)
  -> os_kernel_start_prepare (0x4477D0)
  -> os_thread_create (0x44784E, entry=0x004873F5)
     -> worker fn 0x004873F4
        -> [0x20003DB4 + 0x08] = handle
        -> os_thread_activate (0x447916) / os_thread_close (0x447950)
        -> os_thread_create (0x44784E, entry=0x0048719D)
           -> worker fn 0x0048719C
              -> setup chain: 0x486D94 / 0x486DD0 / 0x486DE4 / 0x486EF8
              -> wait/tick loop: os_event_wait_timeout (0x447A14) + os_tick_now (0x447838) + backedge (`0x48720E` loop)
```

Interpretation:
- Runtime handoff-to-idle mechanics are now anchored through two worker-creation stages.
- OS-wrapper behavior is now named with instruction-backed semantics; naming remains inferred (no vendor symbols).
- Remaining ambiguity is primarily deeper scheduler-core symbolization (`0x452*`/`0x453*` internals), not bootstrap order.
- Evidence: `captures/firmware/analysis/2026-03-05-g2-runtime-entry-chain.md`.

#### 3.2.5 OS Wrapper and Kernel Helper Semantics (`CONFIRMED` behavior, inferred naming)

Recovered wrapper semantics used in the startup-to-idle chain:

| Wrapper | Inferred Symbol | Inferred Role | Key Kernel Helper Callees |
|---:|---|---|---|
| `0x004477A2` | `os_ctx_guard` | execution-context guard (`IPSR`/`PRIMASK`/`BASEPRI`) | `0x00453B30` |
| `0x004477D0` | `os_kernel_start_prepare` | kernel-start gate | `0x00453B30` |
| `0x00447800` | `os_kernel_start_release` | kernel-start release/activate | `0x00452F78` |
| `0x0044784E` | `os_thread_create` | thread create wrapper (static/dynamic paths) | `0x00452AAC`, `0x00452B46` |
| `0x00447916` | `os_thread_activate` | thread activate/resume | `0x00453B28` |
| `0x00447950` | `os_thread_close` | thread close/terminate | `0x00452E14`, `0x00452D3A` |
| `0x00447838` | `os_tick_now` | ISR-aware tick/time read | `0x00453192`, `0x0045318A` |
| `0x00447A14` | `os_event_wait_timeout` | event wait with timeout/mask semantics | `0x00453E10`, `0x0045318A` |
| `0x0044798A` | `os_event_wait` | event wait wrapper (normal/ISR backend switch) | `0x00453ED4`, `0x0045404C` |
| `0x00447DEC` | `os_event_wait_ex` | extended event wait with mode bits | `0x00476F50` |

Evidence:
- `captures/firmware/analysis/2026-03-05-g2-os-wrapper-semantics.md`

#### 3.2.6 Scheduler-Core Helper Lift (`CONFIRMED` behavior, inferred naming)

The wrapper layer now has backend helper semantics with caller evidence outside startup stages:

| Helper | Inferred Symbol | Role |
|---:|---|---|
| `0x00452AAC` | `kernel_thread_create_static` | static control-block thread create |
| `0x00452B46` | `kernel_thread_create_dynamic` | dynamic thread create/alloc path |
| `0x00452BC4` | `kernel_thread_init_core` | thread metadata/list initialization |
| `0x00452C88` | `kernel_thread_ready_insert` | ready-list insertion and scheduler counters |
| `0x00452D3A` | `kernel_thread_terminate` | thread termination/unlink path |
| `0x00452E14` | `kernel_thread_state_classify` | thread-state classification for close gates |
| `0x00453E10` | `kernel_event_wait` | event wait primitive |
| `0x00453ED4` | `kernel_event_op` | event flag set/clear/op primitive |
| `0x0045404C` | `kernel_event_op_isr` | ISR-side event op primitive |
| `0x00476F50` | `kernel_event_wait_ex` | extended event wait primitive |

Cross-domain xref highlights:
- thread create/terminate helpers are used in multiple address regions (`0x0044xxxx`, `0x004Cxxxx`, `0x004Dxxxx`), not only startup stages.
- event helpers (`0x453E10`, `0x453ED4`, `0x45404C`) are also called from `0x0051xxxx` regions, supporting runtime-wide scheduling semantics.

Evidence:
- `captures/firmware/analysis/2026-03-05-g2-scheduler-core-semantics.md`

#### 3.2.7 Stage-2 Idle/Wait Loop Closure (`CONFIRMED` for loop mechanics)

Instruction-level recovery now anchors the steady wait loop in the stage-2 worker and its descriptor-side waiter:

```
dispatch callback load (0x005B415C)
  -> [0x20003DB4] = 0x00487423
  -> stage2 worker domain (analyzed at 0x004871BC)
     -> loop constant load: movw r6, #0xEA60
     -> wait: bl 0x00447A34 (os_event_wait_timeout)
     -> tick: bl 0x00447858 (os_tick_now)
     -> loop backedges:
        0x0048724C -> 0x00487228
        0x00487252 -> 0x0048722E
        0x00487256 -> 0x0048722E
```

Event-lane dispatcher closure (stage-2):
- `0x004872B4` gate shift `26` -> `0x00487074`
- `0x004872FE` gate shift `31` -> `0x00487074`
- `0x00487342` gate shift `30` -> `0x00487074`
- `0x00487386` gate shift `29` -> `0x00487074`
- `0x004873CA` gate shift `28` -> `0x00487074`
- `0x0048740E` gate shift `27` -> `0x00487074`

Descriptor waiter closure:
- `0x00486EB6`: descriptor field read `[base+0x1C]` from literal base `0x20003DB4`
- `0x00486EA6`: `os_event_wait` (`0x004479AA`)
- `0x00486EB8`: `os_event_wait_ex` (`0x00447E0C`)

Evidence:
- `captures/firmware/analysis/2026-03-05-g2-idle-wait-calltree.md`

### 3.3 G2-L vs G2-R Runtime Role Branches (`LIKELY`)

#### G2-L Branch

```
Common startup
  -> master-role branches:
     APP_MasterScanEvent
     APP_MasterConnectEvent
     APP_MasterSysStartTryConnectRing
  -> TinyFrame master mode on inter-eye wired link
  -> sync sends to peer:
     SendInputEventToPeers
     APP_PbTxEncodeScrollSync
```

#### G2-R Branch

```
Common startup
  -> slave-role branches:
     APP_BleSlaveAdvStartEvent
     APP_BleSlaveAsCmdRole
     APP_SlaveStartSecurityRequestEvent
  -> TinyFrame slave mode on inter-eye wired link
  -> audio/ring-relay-heavy runtime threads active
```

Capture-backed runtime signal:
- test runs consistently report `Connected to right eye for audio` (`captures/20260302-2-testAll.txt`, `captures/20260302-3-testAll.txt`), supporting right-eye audio primacy during steady-state user interaction.

Note on ring-side ownership: current artifacts are mixed. Some firmware strings indicate master-side ring connect handling, while device docs/captures also describe right-side ring primacy. Treat exact eye-to-ring ownership as unresolved until live dual-eye + ring traces are decomposed per endpoint identity.

### 3.4 G2 User-Facing BLE Dispatch Path (`CONFIRMED`)

```
Phone writes BLE packet (0x5401 / 0x6401 / 0x7401)
  -> packet routing by service ID (AA envelope)
  -> pb_service_*_common_data_handler
  -> feature subsystem (display/audio/settings/ring/file/OTA)
  -> response/notify on 0x5402 / 0x6402 / 0x7402
```

Representative service handlers (from firmware module map):
- `0x06-20` teleprompt (`pb_service_teleprompt`)
- `0x07-20` EvenAI (`pb_service_even_ai`)
- `0x0D-00/20` settings (`pb_service_setting`)
- `0x0E-20` display config (viewport regions)
- `0xE0-20` EvenHub (container layout engine)
- `0x91-20` ring relay (`pb_service_ring`)
- `0xC4/0xC5` file/OTA transport

### 3.5 G2 Steady-State Idle/Wait to User-Impact Tree (`CONFIRMED` loop core / `LIKELY` service ownership)

```
Scheduler running (no active foreground app transition)
  -> wait on BLE RX queues (thread_ble_msgrx / thread_ble_wsf semaphores)
  -> wait on input events (thread_input; touch + ring relays)
  -> wait on sensor/event-loop queues (fw_evt_loop, sensor_hub)
  -> wait on display driver queue (display_thread / displaydrvmgr)
  -> wait on audio queue (thread_audio)

User-impacting trigger arrives
  -> decode/route (service + command_id/type)
  -> optional inter-eye sync (TinyFrame uart_sync)
  -> optional component callout:
     - display: JBD4010 MSPI
     - touch: CY8C4046FNI path
     - audio: GX8002B host/DMIC path
     - BLE radio state: EM9305 service path
  -> emit ACK/notify packets to phone
  -> return to wait state
```

Practical user-impact examples observed in captures:
- display mode/config + render updates (`0x0E`, `0x06`, `0x07`, `0x0B` traffic families).
- right-eye oriented audio operations.
- ring service discovery and ring command probes in same session.

## 4. G2-Case Boot and Call Trees

### 4.1 Boot to Task Startup (`CONFIRMED` / `PARTIAL`)

```
Power-on / reset
  -> firmware_box vector @ +0x20
     SP=0x20002C88, Reset=0x08000145
  -> reset shim (0x08000144)
     -> preinit thunk (0x080082C6)
     -> startup trampoline (0x080000B8)
        -> ctor walk (0x08000270; table 0x0800D754..0x0800D774)
        -> app main entry (0x0800A3B0)
           -> init sequence:
              0x08004D10, 0x08008250, 0x08006864, 0x0800284C, ...
           -> scheduler handoff sequence:
              0x0800A4DE -> 0x08002F64
              0x0800A4E2 -> 0x0800A6F0
              0x0800A4E6 -> 0x0800678C (task/wait object bring-up)
              0x0800A4EA -> 0x0800A718 (gate) -> 0x0800C09C (scheduler start core)
           -> fallback trap branch if scheduler returns: 0x0800A4EE -> 0x0800A4EE
  -> runtime task/wait domains from 0x0800678C
     -> thread-like entries (0x0800A860 wrapper):
        0x08009B89, 0x0800B965, 0x0800949D, 0x0800B605, 0x0800B9A9, 0x0800A989
     -> queue/wait entries (0x0800A754 wrapper):
        0x08006C41, 0x08007D45, 0x08007025, 0x08008105
     -> queue-domain wait wrappers:
        `0x0800A5EA` (event-bit wrapper), `0x0800A5C8` (context guard), `0x080034FC` (transport wait step)
     -> low-power idle primitive in queue domain:
        `0x08004EE8` (`wfi` at `0x08004EFE`)
  -> standby state machine
     -> IDLE / low battery / glasses-full / cmd-driven standby
```

Anchors:
- Vector + wrapper in `box-case-mcu.md`.
- Reset/startup disassembly and ctor table in `2026-03-05-box-reset-startup-callgraph.md`.
- Scheduler/task bring-up map in `2026-03-05-box-scheduler-task-map.md`.
- Runtime task names from `firmware_box.bin` strings.

### 4.4 Case Task-Domain Idle/Wait Closure (`CONFIRMED` loop core, `LIKELY` wrapper semantics)

```
Queue-domain tasks (0x08007D44 / 0x08007024)
  -> transport wait wrappers (0x080034FC path)
  -> arch idle primitive (0x08004EE8)
     -> wfi @ 0x08004EFE
  -> backedge to task loop head
```

Additional task-loop anchors:
- `0x08007F0C -> 0x08004EE8`, `0x080070D4 -> 0x08004EE8`, `0x08007186 -> 0x08004EE8`.
- Scheduler-start wait setup: `0x0800C0C2 -> 0x0800C81E` before runtime tasking.

### 4.2 Case OTA Path (`CONFIRMED`)

```
Case receives OTA command flow (via glasses relay)
  -> [OTA_BOX] check gls ready
  -> get running bank
  -> erase target bank
  -> copy serial number
  -> read/program firmware chunks
  -> crc_cal vs crc_rx verify
  -> swap bank and reset
```

Additional guards:
- Minimum battery requirement.
- 3-minute timeout paths.
- UART framing/CRC validation (`box_uart_mgr` path on glasses side).

### 4.3 Case-to-User Communication Path (`CONFIRMED`)

```
Case UART status/event
  -> glasses box_uart_mgr parser
  -> glasses case service handlers (glasses_case / box_detect path)
  -> BLE notify back to phone (service 0x81 lane)
  -> app UI updates (battery/charging/in-case state)
```

## 5. R1-Ring Boot and Call Trees

### 5.0 Auxiliary Nordic DFU Boot Vectors, Stage2 Paths, and Idle Anchors (`CONFIRMED` in bundled binaries)

- `B210_BL_DFU_NO_v2.0.3.0004/bootloader.bin` and `B210_ALWAY_BL_DFU_NO/bootloader.bin`:
  - vector bytes: `a0cf0020 d9830f00 ...`
  - decoded: `SP=0x2000CFA0`, `Reset=0x000F83D9` (Thumb)
- `B210_SD_ONLY_NO_v2.0.3.0004/softdevice.bin`:
  - vector bytes: `c0130020 e15f0200 ...`
  - decoded: `SP=0x200013C0`, `Reset=0x00025FE1` (Thumb)

Reset-chain anchors recovered from direct disassembly:
- Bootloader variants share the same reset sequence:
  - `0x000F83D8` -> indirect `blx` to `0x000F9A10` -> tail `bx` to `0x000F8200`
  - stage1 init walker: `0x000F84C8` loop backedge `0x000F84DE -> 0x000F84CE`
  - stage2: `0x000F8200` -> `bl 0x000F84C8` -> tail handoff `0x000FADC8` (versioned) / `0x000FADBC` (always-DFU)
  - stage2 early-call fanout is now recovered in both variants (`0x000FB1xx/0x000FB0xx/0x000FC5xx..0x000FC6xx` families)
- SoftDevice reset chain:
  - pre-reset low-power loop: `0x00025FDC (wfe)` + `0x00025FDE -> 0x00025FDC`
  - `0x00025FE0` -> indirect `blx` to `0x00002FB8` and `0x00025FC8`
  - tail handoff via `0x00026050` to dispatcher entry `0x00001108`

These vectors confirm a Nordic nRF DFU/SoftDevice path exists in bundled assets, but they are separate from Apollo510b main runtime binaries.

### 5.1 Current Evidence Boundary

- No standalone R1 application firmware binary is present in local extracted EVENOTA corpus.
- Nordic DFU bootloader + SoftDevice startup chains (including stage2 call fanout and pre-reset `wfe` idle loop) are now instruction-confirmed, but the ring application runtime call tree below remains `INFERRED` from protocol artifacts (`FE59`, SMP UUID, MCUboot slot-state model, iOSMcuManager lifecycle strings).

### 5.2 Boot and Runtime (`INFERRED`, high confidence on structure)

```
Power-on / reset
  -> MCUboot image manager
     -> inspect slots: bootable/pending/confirmed/active/permanent
     -> select image (active or test image)
     -> jump to ring application
  -> ring app init
     -> initialize BAE80001 service + chars
     -> initialize gesture + health collection modules
     -> enter BLE/event wait loop
        -> notify gesture/battery/state
        -> process phone and/or glasses commands
```

### 5.3 Ring DFU Call Tree (`CONFIRMED protocol flow`)

```
Phone writes FE59 (buttonless DFU trigger)
  -> ring reboots into DFU mode
  -> reconnect to DFU advertisement
  -> SMP upload over DA2E7828-FBCE-4E01-AE9E-261174997C48
  -> image validate/test/confirm operations
  -> reset
  -> MCUboot selects new slot (or rollback if not confirmed)
```

Lifecycle anchor from app RE:
- `none -> requestMcuMgrParameters -> bootloaderInfo -> upload -> validate -> test -> confirm -> reset -> success`.

## 6. Firmware File Usage and Component Communication Matrix

| Firmware File | Loaded/Orchestrated By | Target Component | Transport | User-Visible Effect |
|---|---|---|---|---|
| `ota_s200_bootloader.bin` | Apollo internal boot region | Apollo510b bootloader | Internal flash | Boot decision, OTA install, jump-to-app behavior |
| `ota_s200_firmware_ota.bin` | Bootloader handoff target | Apollo510b main app | Internal flash | All runtime BLE/UI/audio/settings behavior |
| `firmware_ble_em9305.bin` | Main app OTA handler (`service_em9305_dfu`) | EM9305 BLE radio coprocessor | HCI patch records | Radio-layer BLE operation for all phone links |
| `firmware_touch.bin` | Main app touch DFU handler | CY8C4046FNI touch controller | I2C DFU | Touch/gesture events, wear-adjacent touch gating |
| `firmware_codec.bin` | Main app codec DFU/host handlers | GX8002B audio codec | TinyFrame serial/BINH stages | DMIC/I2S audio path and voice features |
| `firmware_box.bin` | Main app box OTA handler | Case MCU | UART relay via glasses | Case battery/charging/in-case status and case OTA |
| Ring firmware (separate package) | Even.app + iOSMcuManager | R1 ring SoC | FE59 + SMP/MCUmgr | Ring gesture/health behavior and ring DFU |

### 6.1 Runtime Component Callout Paths (G2 Main App)

| Trigger Family | Main-App Handler Surface | Internal Component/BUS |
|---|---|---|
| Control services (`0x01..0x22`, `0x80`, `0x91`, `0xFF`) | `pb_service_*_common_data_handler` and related app handlers | EM9305-backed BLE link, inter-eye TinyFrame sync, feature subsystems |
| Display services (`0x0E` config, `0xE0` EvenHub) | EvenHub/navigation/display thread paths | JBD4010 (`drv_mspi_jbd4010.c`, MSPI) |
| Touch/wear input | settings + gesture processor + wear detect | CY8C4046FNI touch path (`drv_cy8c4046fni.c`, I2C) |
| Audio/conversate/evenAI voice | thread_audio + codec host/DFU services | GX8002B codec (`drv_gx8002b.c`, serial/TinyFrame) |
| Case status and case OTA | box detect + `box_uart_mgr` + OTA box processors | Case MCU over UART relay through glasses |
| OTA/file transfer (`0xC4/0xC5`) | ota transport/service processors | staged flash write + downstream subcomponent update handlers |

## 7. User/BLE/API End-to-End Communication

### 7.1 Runtime Interaction (Phone <-> Device)

```
User action in app
  -> app encodes BLE packet (service-specific)
  -> write to glasses/ring BLE characteristic
  -> firmware handler executes
  -> response notify returned
  -> app decodes + updates UI
```

G2 primary channels:
- Control: `0x5401/0x5402`
- Display: `0x6401/0x6402`
- File/OTA: `0x7401/0x7402`

R1 primary runtime channel:
- `BAE80001-...` service (gesture/battery/state path), plus ring relay path through G2 `0x91` service when bridged.

### 7.2 Firmware Update Flow (API -> BLE -> Boot)

```
POST /v2/g/login
  -> JWT token
GET /v2/g/check_latest_firmware
  -> subPath + fileSign
GET https://cdn.evenreal.co{subPath}
  -> EVENOTA binary
BLE file transfer (FILE_CHECK -> START -> DATA -> END)
  -> staged on glasses
bootloader/programming/reboot
  -> main app starts
  -> sub-component updates (box/ble/touch/codec) as needed
```

Current backend contract status in local evidence:
- `GET /v2/g/check_latest_firmware` is the stable successful G2 firmware retrieval path.
- `GET /v2/g/check_firmware` remains unresolved (`1401 Params error` in all local probe matrices).

## 8. Evidence Anchor Index (Offset/Line Backed)

### 8.1 G2 Bootloader -> App Handoff Anchors

| Call-Tree Node | Anchor | Artifact |
|---|---|---|
| Boot target run address load | `bootMetadataInfo.targetRunAddr = 0x%x(0x%x)` @ `140264` | `captures/firmware/g2_extracted/ota_s200_bootloader.bin` |
| No-OTA branch to app | `DO NOT need updata firmware, GO TO APP` @ `141360` | `captures/firmware/g2_extracted/ota_s200_bootloader.bin` |
| Manager startup sync | `thread_manager_sysstart_sync` @ `143388` | `captures/firmware/g2_extracted/ota_s200_bootloader.bin` |
| Jump-to-app log | `APP jumpaddr app(0x%x) = 0x%x` @ `143324` | `captures/firmware/g2_extracted/ota_s200_bootloader.bin` |
| OTA decision gate | `is_need_updata_image` @ `145036` | `captures/firmware/g2_extracted/ota_s200_bootloader.bin` |
| OTA verification path | `app_dfu_image_crc_check` @ `144892`, `_verifyFlashContent` @ `145492` | `captures/firmware/g2_extracted/ota_s200_bootloader.bin` |
| OTA program path | `app_dfu_system_program` @ `144940` | `captures/firmware/g2_extracted/ota_s200_bootloader.bin` |
| Filesystem bring-up | `littlefs_init` @ `146088` | `captures/firmware/g2_extracted/ota_s200_bootloader.bin` |
| VTOR/MSP/BX handoff thunk | file offset `0x1DBDC` (runtime `0x0042DBDC`) | `captures/firmware/analysis/2026-03-03-g2-extracted-wave.md` |
| Main app vector target | `run_base=0x00438000`, `Reset=0x005C9777` | `captures/firmware/analysis/2026-03-03-g2-extracted-wave.md` |

### 8.2 G2 Main-App Startup/Idle Anchors

| Call-Tree Node | Anchor | Artifact |
|---|---|---|
| Reset vector root | `Reset=0x005C9777`, entry `0x005C9776`; recovered startup graph: 16 functions / 15 edges | `captures/firmware/analysis/2026-03-05-g2-reset-startup-callgraph.md` |
| Stack-limit setup | `msr msplim, r0` + `msr psplim, r0` with literal `0x2007D000` @ `0x005C9776` | `captures/firmware/analysis/2026-03-05-g2-reset-startup-disassembly-notes.md` |
| VTOR program stub | `SCB->VTOR = 0x00438000` via `0xE000ED08` @ `0x005C976C` | `captures/firmware/analysis/2026-03-05-g2-reset-startup-disassembly-notes.md` |
| FPU enable block | CPACR update (`OR 0x00F00000`) + `DSB/ISB` + `vmsr fpscr` @ `0x005C97B4` | `captures/firmware/analysis/2026-03-05-g2-reset-startup-disassembly-notes.md` |
| Init-function loop | `blx` bounded init-table walk @ `0x005C97F8` | `captures/firmware/analysis/2026-03-05-g2-reset-startup-disassembly-notes.md` |
| Runtime bootstrap hub | `0x005B4088` call chain + dynamic handoff `blx [0x20003DB4]` | `captures/firmware/analysis/2026-03-05-g2-reset-startup-disassembly-notes.md` |
| Runtime-structure cross refs | additional uses of `0x20003DB4` at `0x0048750C/0x00487520` via `[base+0x1c]` | `captures/firmware/analysis/2026-03-05-g2-reset-startup-disassembly-notes.md` |
| Descriptor xref map | 8 xrefs to `0x20003DB4`, observed offsets `{+0x00,+0x08,+0x1C}` | `captures/firmware/analysis/2026-03-05-g2-dispatch-descriptor-chain.md` |
| Descriptor worker call chain | `0x0048719C -> {0x00486D94,0x00486DD0,0x00486DE4,0x00486EF8}` with wait-loop timing calls | `captures/firmware/analysis/2026-03-05-g2-dispatch-descriptor-chain.md` |
| Sub-descriptor fan-out table | literal table `0x00487548` -> 11 descriptor addresses used by `0x00486E02` | `captures/firmware/analysis/2026-03-05-g2-dispatch-descriptor-chain.md` |
| Init-table effect closure | startup entry sweep (`0x00710830..0x00710878`) with descriptor materialization snapshots | `captures/firmware/analysis/2026-03-05-g2-startup-init-table-effects.md` |
| Root callback (confirmed) | `[0x20003DB4 + 0x00] = 0x00487423` (`0x00487422` worker bootstrap path) | `captures/firmware/analysis/2026-03-05-g2-startup-init-table-effects.md` |
| Post-dispatch runtime chain | `0x00487422 -> 0x004873F4 -> 0x0048719C` with wait/tick loop anchors | `captures/firmware/analysis/2026-03-05-g2-runtime-entry-chain.md` |
| OS-wrapper semantic closure | wrapper naming/evidence map (`os_thread_create`, `os_event_wait_timeout`, etc.) | `captures/firmware/analysis/2026-03-05-g2-os-wrapper-semantics.md` |
| Scheduler-core semantic closure | helper naming + cross-domain caller samples (`0x452*`/`0x453*`) | `captures/firmware/analysis/2026-03-05-g2-scheduler-core-semantics.md` |
| Stage2 wait-loop closure | poll constant `0xEA60`, wait/tick calls (`0x48723A -> 0x447A34`, `0x487240 -> 0x447858`), loop backedges (`0x48724C/0x487252/0x487256`) | `captures/firmware/analysis/2026-03-05-g2-idle-wait-calltree.md` |
| Stage2 event-lane bit gates | dispatch helper `0x487074` callsites with recovered shifts `{26,31,30,29,28,27}` | `captures/firmware/analysis/2026-03-05-g2-idle-wait-calltree.md` |
| Descriptor waiter idle gate | `[0x20003DB4 + 0x1C]` load at `0x486EB6`, `os_event_wait` (`0x486EA6`) + `os_event_wait_ex` (`0x486EB8`) | `captures/firmware/analysis/2026-03-05-g2-idle-wait-calltree.md` |
| Non-returning post-init path | `0x005C9820` loop calling `0x0053AC08` | `captures/firmware/analysis/2026-03-05-g2-reset-startup-disassembly-notes.md` |
| BLE RX thread | `thread_ble_msgrx` @ `3127436` | `captures/firmware/g2_extracted/ota_s200_firmware_ota.bin` |
| BLE TX thread | `thread_ble_msgtx` @ `3127476` | `captures/firmware/g2_extracted/ota_s200_firmware_ota.bin` |
| BLE WSF thread/wait | `thread_ble_wsf` @ `2687928`, `thread_ble_wsf_wait_tx_ready` @ `3019064` | `captures/firmware/g2_extracted/ota_s200_firmware_ota.bin` |
| Input/audio/ring threads | `thread_input` @ `2719008`, `thread_audio` @ `2718560`, `thread_ring` @ `3158852` | `captures/firmware/g2_extracted/ota_s200_firmware_ota.bin` |
| Display runtime thread | `display_thread` @ `3133264` | `captures/firmware/g2_extracted/ota_s200_firmware_ota.bin` |
| BLE handler init | `APP_BleEfsHandlerInit` @ `3091588`, `APP_BleEusHandlerInit` @ `3091660`, `APP_BleNusHandlerInit` @ `3091708`, `APP_BleRingHandlerInit` @ `3091852` | `captures/firmware/g2_extracted/ota_s200_firmware_ota.bin` |
| Role branch markers | `APP_MasterScanEvent` @ `3103276`, `APP_BleSlaveAdvStartEvent` @ `3028116`, `APP_BleSlaveAsCmdRole` @ `3070588`, `APP_SlaveStartSecurityRequestEvent` @ `2941248` | `captures/firmware/g2_extracted/ota_s200_firmware_ota.bin` |
| Idle-loop evidence | `fw_evt_loop_thread_id is NULL` @ `2736124`, `wait_tx_ready success` @ `2718944`, `send idle command to schedule manager` @ `2531028` | `captures/firmware/g2_extracted/ota_s200_firmware_ota.bin` |

### 8.3 G2 Component Handoff Anchors (Main App -> Internal IC/Bus)

| Component Boundary | Anchor | Artifact |
|---|---|---|
| BLE radio DFU path | `service_em9305_dfu.c` @ `2631853`, BLE header parse @ `2530612` | `captures/firmware/g2_extracted/ota_s200_firmware_ota.bin` |
| Touch DFU/input path | `service_touch_dfu.c` @ `2632616`, `service_gesture_processor.c` @ `2631999` | `captures/firmware/g2_extracted/ota_s200_firmware_ota.bin` |
| Audio codec host/DFU path | `codec.dfu` @ `2572133`, codec package info @ `2682760` | `captures/firmware/g2_extracted/ota_s200_firmware_ota.bin` |
| Display driver path | `displaydrv_manager.c` @ `2622277`, `drv_mspi_jbd4010.c` @ `2644620` | `captures/firmware/g2_extracted/ota_s200_firmware_ota.bin` |
| Case relay path | `service_box_detect.c` @ `2589164`, `pt_box_ota_begin` @ `2339800` | `captures/firmware/g2_extracted/ota_s200_firmware_ota.bin` |
| Case relay runtime closure | `0x004B4714` dispatch -> `0x004B4526/0x004B44BE`; BLE send `0x004B451E -> 0x00463178` with `r0=0x81` | `captures/firmware/analysis/2026-03-05-g2-boxdetect-ble-chain.md` |
| Ring relay runtime closure | descriptor slot `0x0067643C=0x91`, handler ptr `0x00676440=0x005B46B1`; wrapper `0x005B46B0 -> 0x005B41FC`; send `0x005B46A4 -> 0x0046F5C4` with `r1=0x91` | `captures/firmware/analysis/2026-03-05-g2-ring-relay-callchain.md` |
| System monitor runtime closure | descriptor slot `0x006764EC=0xFF`, handler ptr `0x006764F0=0x005221D5`; notify `0x005221CC -> 0x00463178` with `r0=0xFF`; idle marker xref `0x005223A8 -> 0x006A1EB4` | `captures/firmware/analysis/2026-03-05-g2-system-monitor-callchain.md` |

### 8.4 G2-Case Boot/Idle/OTA Anchors

| Call-Tree Node | Anchor | Artifact |
|---|---|---|
| Reset vector + startup chain | `0x08000144 -> 0x080000B8 -> 0x08000270 -> 0x0800A3B0` | `captures/firmware/analysis/2026-03-05-box-reset-startup-callgraph.md` |
| Main steady-loop anchor | loop branch at `0x0800A4EE` after init call sequence | `captures/firmware/analysis/2026-03-05-box-reset-startup-callgraph.md` |
| Constructor walk/table | ctor walker `0x08000270`, table `0x0800D754..0x0800D774`, callbacks `0x080002D6`, `0x08009018` | `captures/firmware/analysis/2026-03-05-box-reset-startup-callgraph.md` |
| Scheduler handoff chain | `0x0800A4DE -> 0x08002F64 -> 0x0800A6F0 -> 0x0800678C -> 0x0800A718 -> 0x0800C09C` | `captures/firmware/analysis/2026-03-05-box-scheduler-task-map.md` |
| Task/wait object creation map | six thread-like `0xA860` entries + four queue/wait `0xA754` entries with handle slots (`0x10..0x38`) | `captures/firmware/analysis/2026-03-05-box-scheduler-task-map.md` |
| Task-domain wait wrappers | queue entries call `0x0800A5EA`, `0x0800A5C8`, `0x080034FC` with loop backedges in `0x08006C40/0x08007D44/0x08007024/0x08008104` | `captures/firmware/analysis/2026-03-05-box-scheduler-task-map.md` |
| Task-domain low-power idle | queue tasks call `0x08004EE8` with `wfi` at `0x08004EFE` (`0x08007F0C`, `0x080070D4`, `0x08007186`) | `captures/firmware/analysis/2026-03-05-box-scheduler-task-map.md` |
| Scheduler wait setup | scheduler-start core call `0x0800C0C2 -> 0x0800C81E` (`kernel_wait_queue_wait_ex`) | `captures/firmware/analysis/2026-03-05-box-scheduler-task-map.md` |
| RTOS task creation | `defaultTask` @ `55032`, `pwrManagerTask` @ `55000`, `glsDetectTask` @ `55016`, `ledTask` @ `54992` | `captures/firmware/g2_extracted/firmware_box.bin` |
| Standby/idle behavior | `L fake standby cnt 300s...` @ `29868`, `R fake standby cnt 300s...` @ `29956` | `captures/firmware/g2_extracted/firmware_box.bin` |
| OTA readiness + bank query | `[OTA_BOX]: Check gls ready` @ `5979`, `[OTA_BOX]: Get running bank` @ `6048` | `captures/firmware/g2_extracted/firmware_box.bin` |
| OTA program + CRC verify | `Fail to program` @ `11239`, `crc_cal: 0x%x, crc_rx:0x%x` @ `11507` | `captures/firmware/g2_extracted/firmware_box.bin` |
| Bank swap reset | `Swap bank(2->1) & RESET` @ `14307` | `captures/firmware/g2_extracted/firmware_box.bin` |

### 8.5 R1-Ring Runtime/DFU Anchors

| Call-Tree Node | Anchor | Artifact |
|---|---|---|
| Ring primary runtime service | `BAE80001-4F05-4503-8E65-3AF1F7329D1F [R1 Primary]` | `captures/20260302-2-testAll.txt:350`, `captures/20260302-3-testAll.txt:355` |
| DFU trigger service presence | `FE59 [Unknown]` | `captures/20260302-2-testAll.txt:351`, `captures/20260302-3-testAll.txt:356` |
| Ring scan/connect evidence | `Found ring: EVEN R1_270897` | `captures/20260302-2-testAll.txt:347` |
| Nordic DFU boot vector | `SP=0x2000CFA0`, `Reset=0x000F83D9` | `captures/firmware/B210_BL_DFU_NO_v2.0.3.0004/bootloader.bin` |
| Nordic bootloader reset chain | `0x000F83D8 -> 0x000F9A10 -> 0x000F8200 -> 0x000FADC8/0x000FADBC` | `captures/firmware/analysis/2026-03-05-r1-nordic-dfu-startup-chain.md` |
| Bootloader init-walker loop | `0x000F84DE -> 0x000F84CE` (`blo`) | `captures/firmware/analysis/2026-03-05-r1-nordic-stage2-idle-paths.md` |
| Bootloader stage2 early-call fanout | `0x000FADC8 -> 0x000FB168`, `0x000FADDE -> 0x000FB004`, `0x000FADEA -> 0x000FC654` (and variant peers) | `captures/firmware/analysis/2026-03-05-r1-nordic-stage2-idle-paths.md` |
| SoftDevice vector | `SP=0x200013C0`, `Reset=0x00025FE1` | `captures/firmware/B210_SD_ONLY_NO_v2.0.3.0004/softdevice.bin` |
| SoftDevice pre-reset idle loop | `0x00025FDC (wfe)` + `0x00025FDE -> 0x00025FDC` | `captures/firmware/analysis/2026-03-05-r1-nordic-stage2-idle-paths.md` |
| SoftDevice reset chain | `0x00025FE0 -> {0x00002FB8,0x00025FC8} -> 0x00001108` | `captures/firmware/analysis/2026-03-05-r1-nordic-stage2-idle-paths.md` |

## 9. Service-Resolved Idle -> User-Impact Call Trees (G2)

### 9.1 Common Dispatch Skeleton (`LIKELY`, anchored)

```
Idle wait state (thread_ble_msgrx + thread_ble_wsf + fw_evt_loop)
  -> BLE packet arrives on 0x5401 / 0x6401 / 0x7401
  -> service router picks service ID
  -> *_common_data_handler executes
  -> optional callout to internal component (display/touch/codec/box/ring/BLE radio)
  -> ACK/notify on 0x5402 / 0x6402 / 0x7402
  -> return to queue/semaphore wait
```

Handler anchors in `ota_s200_firmware_ota.bin`:
- `Setting_common_data_handler` @ `3059448`
- `Teleprompt_common_data_handler` @ `3017304`
- `EvenAI_common_data_handler` @ `3036628`
- `Conversate_common_data_handler` @ `2988792`
- `RingDataRelay_common_data_handler` @ `2964504`
- `BoxDetect_common_data_handler` @ `3012536`
- `system_monitor_common_data_handler` @ `2975124`
- `evenhub_common_data_handler` @ `3036880`

### 9.2 Display/User Interface Path (`CONFIRMED` + `LIKELY`)

```
0x6401 display write (phone -> glasses)
  -> evenhub_common_data_handler (3036880)
  -> display_thread queue/dispatcher (3133264)
  -> displaydrv_manager.c path (2622277)
  -> drv_mspi_jbd4010.c (2644620) over MSPI
  -> 0x6402 display notify back to app
```

Direct anchors:
- `menu page recv data from BLE` @ `2524407`
- `[display_thread]...` runtime traces (`display close`, `jump to page`, `startup`)

### 9.3 Settings/Touch/Wear Path (`CONFIRMED` + `LIKELY`)

```
0x5401 settings write (service 0x0D)
  -> Setting_common_data_handler (3059448)
  -> pb_service_setting decode/dispatch
  -> service_touch_dfu.c (2632616) / service_gesture_processor.c (2631999) paths
  -> CY8C4046 touch controller interaction (I2C)
  -> 0x5402 / 0x0D-* notify to app
```

Direct anchors:
- `[pb_service_setting]decode successful...` @ `2608568`
- `[pb_service_setting][Notify]...` @ `2710752`
- touch FW markers in `firmware_touch.bin`: prox baseline @ `30657`, host reset by 5-click @ `30785`

### 9.4 Audio/Conversate/EvenAI Path (`LIKELY`, strong anchors)

```
0x5401 conversate/evenAI/teleprompt writes (0x0B/0x07/0x06 families)
  -> Conversate_common_data_handler / EvenAI_common_data_handler / Teleprompt_common_data_handler
  -> thread_audio scheduling (2718560)
  -> codec.dfu/codec host protocol path
  -> GX8002B transport (TinyFrame/BINH stages)
  -> notify + UI update to phone
```

Direct anchors:
- `Conversate_common_data_handler` @ `2988792`
- `EvenAI_common_data_handler` @ `3036628`
- `Teleprompt_common_data_handler` @ `3017304`
- codec package info @ `2682760`, `codec.dfu` @ `2572133`
- codec FW strings: `start Dmic cmd` @ `78928`, `i2s set state` @ `78971`

### 9.5 Ring Relay Path (`CONFIRMED` lane mechanics, mixed endpoint ownership)

```
0x5401 ring relay write (service 0x91)
  -> runtime descriptor slot (`0x0067643C=0x91`) selects handler pointer (`0x00676440=0x005B46B1`)
  -> wrapper entry `0x005B46B0` (`RingDataRelay_common_data_handler` xrefs)
  -> parser `0x005B41FC` (`APP_PbRxRingFrameDataProcess` xrefs + ring command/event diagnostics)
  -> build/send path `0x005B4506`
  -> outbound relay send `0x005B46A4 -> 0x0046F5C4` with `r1=0x91`
  -> app receives ring-lane response/notify
```

Direct anchors:
- descriptor binding: `0x0067643C=0x00000091`, `0x00676440=0x005B46B1`
- wrapper -> parser call: `0x005B4704 -> 0x005B41FC`
- outbound service-id send: `0x005B46A4 -> 0x0046F5C4` with immediate `r1=0x91`
- `RingDataRelay_common_data_handler` xrefs: `0x005B46CE`, `0x005B471E`
- `APP_PbRxRingFrameDataProcess` xrefs: `0x005B421E`, `0x005B4268`, `0x005B42F6`, `0x005B434E`, `0x005B43B6`
- parser diagnostics: `0x005B4370` (`ring command_id`), `0x005B43D8` (`Unknown command_id`), `0x005B44F0` (`Unknown event_id`), `0x005B473A` (`Unknown event type`)

### 9.6 Case Status / Case OTA Relay Path (`CONFIRMED`)

```
0x5401 case-lane write (service 0x81 family)
  -> BoxDetect dispatch (`0x004B4714`)
     -> status notify branch (`0x004B47D2 -> 0x004B44BE`)
     -> state/apply branch (`0x004B4814/0x004B4856 -> 0x004B4526`)
  -> box_uart_mgr framing/CRC path (3132656)
  -> UART exchange with case MCU
  -> BLE notify send wrapper (`0x004B451E -> 0x00463178`, service id `0x81`)
  -> case state/OTA result propagated to app
```

Direct anchors:
- `BoxDetect_common_data_handler` @ `3012536`
- `box_uart_mgr` @ `3132656`
- box UART error/CRC markers around `2542560`, `2907976`, `3005720`
- BoxDetect handler-string xrefs in dispatch path: `0x004B4754`, `0x004B47A8`, `0x004B47EA`, `0x004B482C`, `0x004B4872` -> `0x00717798`
- case-sync message xref in dispatch: `0x004B4822 -> 0x007177B8`
- command split in dispatcher: `cmp r0,#1/#3` with branches into `0x004B44BE` vs `0x004B4526`
- BLE lane closure: `0x004B451E -> 0x00463178` with recovered `r0=0x81`
- auxiliary edge retained for follow-up lift: `0x00545866 -> 0x00543E06`

### 9.7 System Monitor Idle Loop Path (`CONFIRMED`)

```
system event/control write (0xFF family)
  -> runtime descriptor slot (`0x006764EC=0xFF`) selects handler pointer (`0x006764F0=0x005221D5`)
  -> monitor notify sender `0x00522184` (caller `0x004D0972`)
  -> BLE send `0x005221CC -> 0x00463178` with `r0=0xFF` (probe payload `55 04 12 34 56 78`)
  -> handler `0x005221D4` (`system_monitor_common_data_handler` xrefs)
  -> idle marker load `0x005223A8 -> 0x006A1EB4` (`send idle command to schedule manager`)
  -> scheduler returns system to low-activity wait state
```

Direct anchors:
- descriptor binding: `0x006764EC=0x000000FF`, `0x006764F0=0x005221D5`
- notify bridge caller: `0x004D0972 -> 0x00522184`
- BLE send closure: `0x005221CC -> 0x00463178` with immediate `r0=0xFF`
- `system_monitor_common_data_handler` xrefs: `0x005221F0`, `0x00522262`, `0x005222A2`, `0x005222E2`, `0x0052232C`, `0x0052238C`
- idle command marker xref: `0x005223A8 -> 0x006A1EB4`

## 10. Cross-Version Stability Snapshot (Boot + Component Boundaries)

Source: `captures/firmware/analysis/2026-03-03-hardware-functionality-mapping.json` (`marker_presence`).

| Marker | `2.0.1.14` | `2.0.3.20` | `2.0.5.12` | `2.0.6.14` | `2.0.7.16` | Stable |
|---|---:|---:|---:|---:|---:|---|
| `bootMetadataInfo.targetRunAddr...` | 139756 | 139980 | 140196 | 140196 | 140264 | Yes |
| `APP jumpaddr app...` | 142820 | 143004 | 143256 | 143256 | 143324 | Yes |
| `ota/s200_firmware_ota.bin` | 143652 | 143836 | 144088 | 144088 | 144156 | Yes |
| `service_em9305_dfu.c` | 2149228 | 2565384 | 2631424 | 2649716 | 2631853 | Yes |
| `service_touch_dfu.c` | 2149807 | 2566539 | 2632651 | 2651159 | 2632616 | Yes |
| `service_box_detect.c` | 2141795 | 2546895 | 2608815 | 2626535 | 2589164 | Yes |
| `drv_mspi_jbd4010.c` | 2175667 | 2579651 | 2647395 | 2666039 | 2644620 | Yes |
| codec package info marker | 2180428 | 2588172 | 2658092 | 2677144 | 2682760 | Yes |

Interpretation: boot handoff, service-to-component boundaries, and core peripheral ownership remain structurally stable across all locally recovered production versions.

## 11. Open Reverse-Engineering Gaps

1. Full symbolized reset-handler/runtime handoff graph is not fully closed: reset path through `0x005C9776 -> ... -> 0x005B4088 -> blx [0x20003DB4]` is recovered, callback initialization for `[0x20003DB4 + 0x00]` is confirmed (`0x00487423`), post-dispatch chain (`0x00487422 -> 0x004873F4 -> 0x0048719C`) is anchored, and stage2 idle-loop mechanics are now instruction-confirmed (`0x48723A/0x487240` wait/tick + loop backedges), but semantic naming for deeper scheduler/helper families remains incomplete.
2. Exact fixed eye ownership for ring connection logic remains mixed in current artifacts.
3. No direct R1 ring application binary disassembly is in this corpus yet; ring runtime tree remains protocol-inferred even though bundled Nordic bootloader/SoftDevice startup+idle anchors are instruction-confirmed (`0x000F83D8`/`0x000F84C8`/`0x00025FDC` paths).
4. On-radio internals inside `firmware_ble_em9305.bin` remain opaque beyond record-table structure.
