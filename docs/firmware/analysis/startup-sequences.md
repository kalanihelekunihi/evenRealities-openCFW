# Firmware Startup Sequences

> Analysis performed 2026-03-05. Firmware binaries from `captures/firmware/g2_extracted/`.

---

## 1. G2 Main Firmware Startup

### 1.1 Reset Vector and Callgraph

Firmware: `captures/firmware/g2_extracted/ota_s200_firmware_ota.bin`

#### Image Metadata

- `run_base`: `0x00438000`
- `vector_sp`: `0x2007FB00`
- `vector_reset`: `0x005C9777` (entry `0x005C9776`)
- `image_range`: `0x00438000` - `0x0074299F`
- `analysis_depth`: `4`

#### Root Summary

- root function `0x005C9776`: 5 instructions, 1 calls, 0 branch targets

#### Call Edges

| Depth | Caller | Callee |
|---:|---:|---:|
| 0 | `0x005C9776` | `0x005C9798` |
| 1 | `0x005C9798` | `0x005C97B4` |
| 1 | `0x005C9798` | `0x005C97D8` |
| 2 | `0x005C97D8` | `0x005B4088` |
| 2 | `0x005C97D8` | `0x005C976C` |
| 2 | `0x005C97D8` | `0x005C97F8` |
| 2 | `0x005C97D8` | `0x005C9820` |
| 3 | `0x005B4088` | `0x0043CCC8` |
| 3 | `0x005B4088` | `0x0043CD6C` |
| 3 | `0x005B4088` | `0x0043D1C8` |
| 3 | `0x005B4088` | `0x00468D9E` |
| 3 | `0x005B4088` | `0x004A8BB6` |
| 3 | `0x005B4088` | `0x005A41F0` |
| 3 | `0x005B4088` | `0x005B3DE0` |
| 3 | `0x005C9820` | `0x0053AC08` |

#### Recovered Functions

| Function | Depth | Instr | Calls | Branch Targets | Returns | Truncated |
|---:|---:|---:|---:|---:|---:|---|
| `0x0043CCC8` | 4 | 62 | 9 | 8 | 1 | false |
| `0x0043CD6C` | 4 | 3 | 0 | 0 | 1 | false |
| `0x0043D1C8` | 4 | 400 | 16 | 27 | 1 | true |
| `0x00468D9E` | 4 | 34 | 4 | 3 | 1 | false |
| `0x004A8BB6` | 4 | 5 | 1 | 0 | 1 | false |
| `0x0053AC08` | 4 | 7 | 0 | 1 | 0 | false |
| `0x005A41F0` | 4 | 30 | 2 | 4 | 1 | false |
| `0x005B3DE0` | 4 | 261 | 4 | 38 | 1 | false |
| `0x005B4088` | 3 | 88 | 7 | 10 | 0 | false |
| `0x005C976C` | 3 | 5 | 0 | 0 | 1 | false |
| `0x005C9776` | 0 | 5 | 1 | 0 | 1 | false |
| `0x005C9798` | 1 | 19 | 2 | 0 | 1 | false |
| `0x005C97B4` | 2 | 10 | 0 | 0 | 1 | false |
| `0x005C97D8` | 2 | 26 | 4 | 3 | 1 | false |
| `0x005C97F8` | 3 | 16 | 0 | 2 | 1 | false |
| `0x005C9820` | 3 | 5 | 1 | 2 | 0 | false |

#### Root Instruction Sample

```asm
0x005C9776: ldr      r0, [pc, #0x18]
0x005C9778: msr      msplim, r0
0x005C977C: msr      psplim, r0
0x005C9780: bl       #0x5c9798
0x005C9784: bx       lr
```

### 1.2 Reset Startup Disassembly Notes

Method: Capstone Thumb/M-profile disassembly from `.venv-re`.

#### 1) Reset Entry and Stack-Limit Setup (`0x005C9776`)

```asm
0x005C9776: ldr      r0, [pc, #0x18]   ; literal @0x005C9790 = 0x2007D000
0x005C9778: msr      msplim, r0
0x005C977C: msr      psplim, r0
0x005C9780: bl       #0x5c9798
0x005C9784: bx       lr
```

#### 2) App VTOR Program Stub (`0x005C976C`)

```asm
0x005C976C: ldr      r0, [pc, #0x18]   ; literal @0x005C9788 = 0x00438000
0x005C976E: ldr      r1, [pc, #0x1c]   ; literal @0x005C978C = 0xE000ED08 (SCB->VTOR)
0x005C9770: str      r0, [r1]
0x005C9772: movs     r0, #1
0x005C9774: bx       lr
```

#### 3) FPU/CPACR Enable Block (`0x005C97B4`)

```asm
0x005C97B4: movw     r1, #0xed88
0x005C97B8: movt     r1, #0xe000
0x005C97BC: ldr      r0, [r1]
0x005C97BE: orr      r0, r0, #0xf00000
0x005C97C2: str      r0, [r1]
0x005C97C4: dsb      sy
0x005C97C8: isb      sy
0x005C97CC: mov.w    r0, #0x2040000
0x005C97D0: vmsr     fpscr, r0
0x005C97D4: bx       lr
```

#### 4) Startup Dispatcher (`0x005C97D8`)

```asm
0x005C97D8: bl       #0x5c976c
0x005C97DC: cmp      r0, #0
0x005C97DE: beq      #0x5c97e4
0x005C97E0: bl       #0x5c97f8
...
0x005C97EE: bl       #0x5b4088
0x005C97F2: bl       #0x5c9820
```

#### 5) Init-Array-Like Loop (`0x005C97F8`)

```asm
0x005C97F8: push     {r4, lr}
0x005C97FA: ldr      r1, [pc, #0x1c]   ; literal @0x005C9818 = 0x00147018
0x005C97FC: add      r1, pc
0x005C97FE: adds     r1, #0x18
0x005C9800: ldr      r4, [pc, #0x18]   ; literal @0x005C981C = 0x0014705C
0x005C9802: add      r4, pc
0x005C9804: adds     r4, #0x16
0x005C9808: ldr      r2, [r1]
0x005C980A: adds     r0, r1, #4
0x005C980C: add      r1, r2
0x005C980E: blx      r1
0x005C9812: cmp      r1, r4
0x005C9814: bne      #0x5c9808
0x005C9816: pop      {r4, pc}
```

Interpretation: looped indirect calls over a bounded table region before the main runtime bootstrap.

#### 6) Post-Init Trap/Exit Loop (`0x005C9820`)

```asm
0x005C9820: b.w      #0x5c9824
0x005C9824: mov      r7, r0
0x005C9826: mov      r0, r7
0x005C9828: bl       #0x53ac08
0x005C982C: b        #0x5c9826
```

#### 7) Runtime Bootstrap Hub (`0x005B4088`)

```asm
0x005B4088: push     {lr}
0x005B408C: movs     r0, #0xc8
0x005B408E: bl       #0x4a8bb6
0x005B4092: bl       #0x5a41f0
...
0x005B40CA: bl       #0x43ccc8
0x005B40CE: bl       #0x5b3de0
...
0x005B4158: bl       #0x468d9e
0x005B415C: ldr      r0, [pc, #0x98]   ; literal @0x005B41F8 = 0x20003DB4
0x005B415E: ldr      r0, [r0]
0x005B4160: blx      r0
0x005B4162: b        #0x5b4162
```

Interpretation: this block performs platform bring-up/checks and then dispatches through a RAM function pointer (`[0x20003DB4]`) into the next-stage runtime entry.

#### 8) Additional `0x20003DB4` Cross-References (`PARTIAL`)

Besides the startup handoff at `0x005B415C`, another literal pool references `0x20003DB4` at `0x00487530`.

Observed accessors:

```asm
0x0048750C: ldr      r0, [pc, #0x20]   ; literal @0x00487530 = 0x20003DB4
0x0048750E: ldr      r0, [r0, #0x1c]
0x00487510: bl       #0x447d36

0x00487520: ldr      r0, [pc, #0xc]    ; literal @0x00487530 = 0x20003DB4
0x00487522: ldr      r0, [r0, #0x1c]
0x00487524: bl       #0x447d36
```

Literal table words beginning at `0x00487530`:

- `0x20003DB4`
- `0x004A0A87`
- `0x004A092D`
- `0x0049B8B1`
- `0x00462A1B`
- `0x00448A03`

Interpretation: `0x20003DB4` behaves like a runtime control/dispatch structure accessed both at boot handoff (`[base+0]`) and steady-state helper paths (`[base+0x1c]`).

#### 9) Consolidated Descriptor Xref Map

Recovered load sites for literal `0x20003DB4`:
- `0x00486D96` -> writes/reads `[+0x1C]`
- `0x00486E92` -> reads `[+0x1C]`
- `0x004870AE` -> reads `[+0x1C]`
- `0x004873F6` -> writes `[+0x08]`
- `0x0048744C` -> reads `[+0x08]`
- `0x0048750C` -> reads `[+0x1C]`
- `0x00487520` -> reads `[+0x1C]`
- `0x005B415C` -> startup reads `[+0x00]` then `blx r0`

Observed field offsets: `+0x00`, `+0x08`, `+0x1C`.

### 1.3 Runtime Entry Chain (Post-Dispatch)

#### Dispatch Entry Closure

- startup handoff site: `0x005B415C` reads `[0x20003DB4]` then `blx`
- confirmed callback pointer: `0x00487423` (entry `0x00487422`)

#### Bootstrap Chain

| Stage | Function | Key Direct Calls |
|---|---:|---|
| dispatch-entry | `0x00487422` | 0x004477D0, 0x0044784E, 0x005D6CDC, 0x00447800 |
| stage1-worker-bootstrap | `0x004873F4` | 0x0044784E, 0x005D6CDC, 0x00447916, 0x00447950 |
| stage2-supervisor-loop | `0x0048719C` | 0x00486D94, 0x00486DD0, 0x00486DE4, 0x00486EF8, 0x0043CD6C, 0x0043D1C8, 0x0043CD6C, 0x0043CD6C, 0x0043CCC8, 0x00487238, 0x00447A14, 0x00447838 |
| stage2-descriptor-waiter | `0x00486E7A` | 0x0044798A, 0x00447DEC, 0x0043CD6C, 0x0043D1C8, 0x0043CD6C, 0x0043CD6C, 0x0043CCC8 |

#### Thread-Create Anchors

| Caller | Create Callsite | Worker Entry Ptr | Worker Entry Fn |
|---:|---:|---:|---:|
| `0x00487422` | `0x0048742E` | `0x004873F5` | `0x004873F4` |
| `0x004873F4` | `0x004873FE` | `0x0048719D` | `0x0048719C` |

#### Wait/Idle Loop Anchors

- wait calls (`0x447A14`) in stage2: 0x0048721A
- tick/time calls (`0x447838`) in stage2: 0x00487220
- backedges in stage2: `0x0048722C -> 0x00487208`, `0x00487232 -> 0x0048720E`, `0x00487236 -> 0x0048720E`

#### Descriptor Seed Snapshot (Init-Table Output)

| Address | Value |
|---:|---:|
| `0x20000614` | `0x004FCCF5` |
| `0x200034A0` | `0x004AE4A1` |
| `0x20003C60` | `0x00524BD9` |
| `0x20003CBC` | `0x0049B5FD` |
| `0x20003CE0` | `0x0046EDF9` |
| `0x20003D04` | `0x00456EFB` |
| `0x20003D28` | `0x0045977B` |
| `0x20003D4C` | `0x004EDAE9` |
| `0x20003D70` | `0x004FD765` |
| `0x20003D74` | `0x004FD8D9` |
| `0x20003D94` | `0x00000000` |
| `0x20003D98` | `0x004FDAD3` |
| `0x20003DA0` | `0x004FDADB` |
| `0x20003DA8` | `0x004FDAE5` |
| `0x20003DB0` | `0x004FDA85` |
| `0x20003DB4` | `0x00487423` |
| `0x20003DB8` | `0x0048744B` |
| `0x20003DBC` | `0x00000000` |
| `0x20003DD0` | `0x00000000` |
| `0x20003DD8` | `0x0052C157` |
| `0x20003DFC` | `0x004BDA25` |

#### Interpretation

- `0x00487422` is now a confirmed runtime bootstrap entry that creates stage1 worker `0x004873F5`.
- Stage1 (`0x004873F4`) binds runtime handle state at `[0x20003DB4 + 0x08]` and starts its worker lane.
- Stage2 (`0x0048719C`) repeatedly executes wait/tick loop primitives (`0x447A14`, `0x447838`), matching idle/event-wait behavior.

### 1.4 Startup Init-Table Effects (Emulated)

#### Image Metadata

- `run_base`: `0x00438000`
- `vector_reset`: `0x005C9777`
- `init_loop`: `0x005C97F8`
- `table_start`: `0x00710830`
- `table_end`: `0x00710878`

#### Entry Execution

| Index | Entry Ptr | Handler | Kind | Descriptor `[0x20003DB4]` Before -> After |
|---:|---:|---:|---|---|
| `0` | `0x00710830` | `0x005D6C57` | `zero` | `0x00000000` -> `0x00000000` |
| `1` | `0x00710848` | `0x0043A11F` | `lz` | `0x00000000` -> `0x00000000` |
| `2` | `0x00710858` | `0x0043A11F` | `lz` | `0x00000000` -> `0x00487423` |
| `3` | `0x00710868` | `0x0043A11F` | `lz` | `0x00487423` -> `0x00487423` |

#### Confirmed Dispatch Callback

- `[0x20003DB4]` after init-table execution: `0x00487423`
- expected callback pointer: `0x00487423` (entry function `0x00487422`)
- callback pointer match: `true`

#### Descriptor Probe Snapshot

| Address | Value |
|---:|---:|
| `0x20000614` | `0x004FCCF5` |
| `0x200034A0` | `0x004AE4A1` |
| `0x20003C60` | `0x00524BD9` |
| `0x20003C64` | `0x00524D29` |
| `0x20003CBC` | `0x0049B5FD` |
| `0x20003CC0` | `0x0049B629` |
| `0x20003CE0` | `0x0046EDF9` |
| `0x20003CE4` | `0x0046EE25` |
| `0x20003D04` | `0x00456EFB` |
| `0x20003D08` | `0x00456F27` |
| `0x20003D28` | `0x0045977B` |
| `0x20003D2C` | `0x004597A1` |
| `0x20003D4C` | `0x004EDAE9` |
| `0x20003D50` | `0x004EDB15` |
| `0x20003D70` | `0x004FD765` |
| `0x20003D74` | `0x004FD8D9` |
| `0x20003D94` | `0x00000000` |
| `0x20003D98` | `0x004FDAD3` |
| `0x20003D9C` | `0x00000001` |
| `0x20003DA0` | `0x004FDADB` |
| `0x20003DA4` | `0x00000002` |
| `0x20003DA8` | `0x004FDAE5` |
| `0x20003DAC` | `0x00000003` |
| `0x20003DB0` | `0x004FDA85` |
| `0x20003DB4` | `0x00487423` |
| `0x20003DB8` | `0x0048744B` |
| `0x20003DBC` | `0x00000000` |
| `0x20003DC0` | `0x00000000` |
| `0x20003DC4` | `0x00000000` |
| `0x20003DD0` | `0x00000000` |
| `0x20003DD8` | `0x0052C157` |
| `0x20003DDC` | `0x0052C187` |
| `0x20003DFC` | `0x004BDA25` |
| `0x20003E00` | `0x004BDA51` |

#### Notes

- The startup loop materializes the runtime dispatch structure before `0x005B415C` performs `ldr r0, [0x20003DB4]; blx r0`.
- Emulation confirms the root callback is `0x00487423` (entry `0x00487422`), upgrading prior status from likely to confirmed.

---

## 2. G2 Case (Box) Startup

Firmware: `captures/firmware/g2_extracted/firmware_box.bin`

### 2.1 Vector and Reset

- stack pointer: `0x20002C88`
- reset vector: `0x08000145` (entry `0x08000144`)

### 2.2 Boot Chain

```
Reset entry
  -> preinit thunk: 0x080082C6
  -> startup trampoline: 0x080000B8
     -> ctor walk: 0x08000270
     -> app main: 0x0800A3B0
        -> init call sequence ...
        -> steady loop at 0x0800A4EE
```

### 2.3 Main Init Call Sequence

| Callsite | Callee |
|---:|---:|
| `0x0800A3B2` | `0x08004D10` |
| `0x0800A3B6` | `0x08008250` |
| `0x0800A3BA` | `0x08006864` |
| `0x0800A3BE` | `0x0800284C` |
| `0x0800A3C2` | `0x080069D4` |
| `0x0800A3C6` | `0x08006A24` |
| `0x0800A3CA` | `0x08006714` |
| `0x0800A3D0` | `0x08004824` |
| `0x0800A3EC` | `0x08008F88` |
| `0x0800A3F2` | `0x08008F88` |
| `0x0800A40C` | `0x08004A18` |
| `0x0800A410` | `0x08004990` |
| `0x0800A416` | `0x08004890` |
| `0x0800A41A` | `0x08004960` |
| `0x0800A41E` | `0x08004974` |
| `0x0800A422` | `0x08004944` |
| `0x0800A434` | `0x08008F88` |
| `0x0800A43A` | `0x08008F88` |
| `0x0800A47C` | `0x08008F88` |
| `0x0800A482` | `0x08008F88` |
| `0x0800A4A0` | `0x08008F88` |
| `0x0800A4A6` | `0x08008F88` |
| `0x0800A4BC` | `0x08008F88` |
| `0x0800A4C2` | `0x08008F88` |

### 2.4 Constructor Table (from ctor walk literals)

- table range: `0x0800D754 .. 0x0800D774`

| Entry | arg0 | arg1 | arg2 | callback |
|---:|---:|---:|---:|---:|
| `0x0800D754` | `0x0800D774` | `0x20000000` | `0x000001A4` | `0x080002D6` |
| `0x0800D764` | `0x0800D7DC` | `0x200001A4` | `0x00002AE4` | `0x08009018` |

### 2.5 Interpretation

- Case boot is now anchored as reset -> startup trampoline -> constructor table walk -> app main.
- `0x0800A3B0` performs peripheral/service bring-up then transitions into an explicit steady loop at `0x0800A4EE`.
- This gives instruction-level evidence for the case path from reset to idle/wait state.

---

## 3. R1 Ring Startup

### 3.1 Nordic DFU Binary Startup Chains

#### Vector Summary

| Image | Base | SP | Reset | Entry | Size |
|---|---:|---:|---:|---:|---:|
| B210_BL_DFU_NO_v2.0.3.0004 bootloader | `0x000F8000` | `0x2000CFA0` | `0x000F83D9` | `0x000F83D8` | 24420 |
| B210_ALWAY_BL_DFU_NO bootloader | `0x000F8000` | `0x2000CFA0` | `0x000F83D9` | `0x000F83D8` | 24180 |
| B210_SD_ONLY_NO_v2.0.3.0004 softdevice | `0x00001000` | `0x200013C0` | `0x00025FE1` | `0x00025FE0` | 153140 |

#### Reset Chains

##### B210_BL_DFU_NO_v2.0.3.0004 bootloader

- reset entry: `0x000F83D8`
- indirect reset calls: 0x000F83DA -> 0x000F9A10
- reset tail handoff: `0x000F83DE -> 0x000F8200`
- stage2 entry: `0x000F8200`
- stage2 immediate calls: 0x000F8204 -> 0x000F84C8
- stage2 tail handoff: `0x000F820A -> 0x000FADC8`

##### B210_ALWAY_BL_DFU_NO bootloader

- reset entry: `0x000F83D8`
- indirect reset calls: 0x000F83DA -> 0x000F9A10
- reset tail handoff: `0x000F83DE -> 0x000F8200`
- stage2 entry: `0x000F8200`
- stage2 immediate calls: 0x000F8204 -> 0x000F84C8
- stage2 tail handoff: `0x000F820A -> 0x000FADBC`

##### B210_SD_ONLY_NO_v2.0.3.0004 softdevice

- reset entry: `0x00025FE0`
- indirect reset calls: 0x0002600E -> 0x00002FB8, 0x00026012 -> 0x00025FC8
- reset tail handoff: `0x00026050 -> 0x00001108`
- stage2 entry: `0x00001108`
- stage2 immediate calls: 0x00001108 -> 0x00001110, 0x0000110C -> 0x00025FBE, 0x00001122 -> 0x00025FBE

#### Interpretation

- Both bundled bootloader variants share the same reset chain (`0x000F83D8 -> 0x000F9A10 -> 0x000F8200`), then hand off deeper into bootloader main (`0x000FADC8`).
- SoftDevice startup at `0x00025FE0` performs MSP/guard setup and calls helper entries (`0x00002FB8`, `0x00025FC8`) before reaching SVC/dispatcher handoff (`0x00001108`).
- This confirms instruction-level Nordic DFU binary boot chains even though standalone R1 application firmware remains unavailable.

### 3.2 Stage2 and Idle/Wait Paths

#### Bootloader Variants

##### B210_BL_DFU_NO_v2.0.3.0004 bootloader

- reset chain: `0x000F83D8` -> `0x000F8200` -> `0x000FADC8`
- stage1 init walker call: `0x000F8204 -> 0x000F84C8`
- stage1 tail handoff: `0x000F820A -> 0x000FADC8`
- init walker loop backedge(s):
  - `0x000F84DE -> 0x000F84CE` (blo)
- stage2 early calls:
  - `0x000FADC8 -> 0x000FB168`
  - `0x000FADD2 -> 0x000FB004`
  - `0x000FADDE -> 0x000FB004`
  - `0x000FADE6 -> 0x000FB0B8`
  - `0x000FADEA -> 0x000FC654`
  - `0x000FADFA -> 0x000F82AE`

##### B210_ALWAY_BL_DFU_NO bootloader

- reset chain: `0x000F83D8` -> `0x000F8200` -> `0x000FADBC`
- stage1 init walker call: `0x000F8204 -> 0x000F84C8`
- stage1 tail handoff: `0x000F820A -> 0x000FADBC`
- init walker loop backedge(s):
  - `0x000F84DE -> 0x000F84CE` (blo)
- stage2 early calls:
  - `0x000FADBC -> 0x000FB0BC`
  - `0x000FADC6 -> 0x000FAF74`
  - `0x000FADD2 -> 0x000FAF74`
  - `0x000FADDA -> 0x000FB028`
  - `0x000FADDE -> 0x000FC568`
  - `0x000FADEE -> 0x000F82AE`

#### SoftDevice

- reset entry: `0x00025FE0` with tail dispatch to `0x00001108`
- pre-reset low-power wait loop: `0x00025FDC (wfe)` + `0x00025FDE -> 0x00025FDC`
- reset indirect calls:
  - `0x0002600E -> 0x00002FB8` (blx via r0, ptr `0x00002FB9`)
  - `0x00026012 -> 0x00025FC8` (blx via r0, ptr `0x00025FC9`)
- dispatcher-entry early calls:
  - `0x00001108 -> 0x00001110`
  - `0x0000110C -> 0x00025FBE`
  - `0x00001122 -> 0x00025FBE`

#### Interpretation

- Bootloader stage1 performs constructor/init-table walking before handing off into stage2 DFU/runtime logic.
- SoftDevice has an explicit `wfe` low-power idle loop in the pre-reset gate path, giving concrete wait-state evidence in bundled R1 binaries.
- Ring application runtime is still out-of-corpus, but Nordic bootloader + SoftDevice now include instruction-level startup and wait anchors.
