# G2 audio, codec-link, clock/power and RTOS findings (Apollo main, stock 2.2.6.10)

Distilled on 2026-10-21 from the removed `g2/analysis/audio-*` experiment
directories (2026-10-06 … 2026-10-10). Originals are recoverable with
`git show pre-consolidation:g2/analysis/<dir>/<file>` (or `git checkout pre-consolidation -- g2/analysis/<dir>`).
All addresses are Apollo510 main-image Thumb entries (raw load `0x438000`) or SRAM/MMIO; "stock" means the locked OTA bytes.
Behaviour was established by original-instruction emulation against synthetic state, not hardware; physical timing/readiness is never implied.

Terminology: in these sources **"PCM0.7/2.0/2.1/2.2" is Ambiq's SPOT-manager *power-control-module* family** (`am_hal_spotmgr_pcm*.c`), not audio PCM. "PCM registration/consumer" (§2) is audio PCM.

Citation form: every source is `pre-consolidation:g2/analysis/<dir>/<file>`; where a table cell lists only `<dir>/<file>`, the same prefix applies.

---

## 1. Audio task, message queue and dispatcher

### 1.1 Thread and resources

| Item | Value | Source |
|---|---|---|
| Thread init | `0x53C344` → `osThreadNew 0x4490E2(handler 0x53C52D, NULL, attr 0x75B8C8)` | pre-consolidation:g2/analysis/audio-task-configuration-closure-2026-10-08/REPORT.md |
| Attributes | name `audio` (`0x78EBB4`), attr bits 0, static CB `0x20072300`/112 B, stack `0x20360E18`/8192 B (2048 words), priority **47**, TZ module 1 | same |
| Context block `0x20003F98` | `+0` initializer `0x53C345`, `+4` terminator `0x53C4F3`, `+8` thread handle, `+12` queue handle (queue global `0x20003FA4`) | same; pre-consolidation:g2/analysis/audio-watchdog-callback-closure-2026-10-09/REPORT.md |
| Queue | `0x53C3EE`: `osMessageQueueNew 0x449A32(50, 12, NULL)` → dynamic `0x441636`, `malloc(680)` = 80-B object + 600-B storage (heap minimum block 696) | audio-task-configuration-closure-2026-10-08/REPORT.md; pre-consolidation:g2/analysis/audio-timer-aux-lifetime-closure-2026-10-08/REPORT.md |
| Handler | runs counter-reset / codec-mode / resource init, then waits low-24 flags forever; flag dispatcher `0x53CDAC`: bit22 `0x400000` → drain loop `0x53CD62` (zero-timeout get + dispatch), bit23 `0x800000` → `AUD_ThreadExit 0x53CDC2` (bit22 first if both) | pre-consolidation:g2/analysis/audio-thread-flags-closure-2026-10-08/REPORT.md |
| Terminate | `0x53C4F2` → `osThreadTerminate 0x4491FE`; static TCB/stack never freed | audio-task-configuration-closure-2026-10-08/REPORT.md |

### 1.2 Message format, publisher and dispatch

- Message is 12 bytes `{u32 type, u32 mode, u32 value}`; dispatcher compares **low 16 bits** of type; callbacks use **low 8 bits** of value (256 aliases 0). (pre-consolidation:g2/analysis/audio-control-callbacks-closure-2026-10-08/REPORT.md)
- Publisher `AUD_SendMessage 0x53C638` (122 B): rejects NULL msg/queue; `osMessageQueuePut 0x449ABE` prio 0 timeout 0; on success `osThreadFlagsSet 0x449238(thread, 0x400000)`; on failure logs via `0x43D0CE`/`0x43D574`/`0x43CE9E`. Flags carry no PCM pointer/ownership token. (pre-consolidation:g2/analysis/audio-source-candidate-20261010/REPORT.md; pre-consolidation:g2/analysis/audio-notification-pcm-2026-10-06/REPORT.md)
- Dispatcher `0x53C5AC` scans 8 rows (stride 8: `u16 type, u16 pad, Thumb fn`) at **`0x20003FBC`** (literal `0x53CEB4`; older reports wrongly said `0x20073FBC`). Table comes from the startup low-RAM record (§9). No row for type 7. (pre-consolidation:g2/analysis/audio-dispatch-initializer-closure-2026-10-08/REPORT.md; pre-consolidation:g2/analysis/audio-notification-wake-closure-2026-10-08/REPORT.md)

| Type | Callback | Role |
|---|---|---|
| 0 | `0x53C860` | codec/DSP control (see below) |
| 1 | `0x53C7B0` | PDM control |
| 2 | `0x53C6F2` | PCM-ready consumer (§2.3) |
| 3 | `0x53C776` | — |
| 4 | `0x53C9FA` | — |
| 5 | `0x53CA72` | — |
| 6 | `0x53C92E` | watchdog check (§1.3) |
| 8 | `0x53CCA6` | — |

Type-0/1 routing (role byte `0x200038F1` via getter `0x4ABE60`; variant byte `0x20075019`) — source pre-consolidation:g2/analysis/audio-control-callbacks-closure-2026-10-08/REPORT.md:

| Callback / condition | Behaviour |
|---|---|
| Type0, role 1 | value≠0 → DSP enable `0x57D6B4`; 0 → DSP disable `0x57D794` (then gate/I2S) |
| Type0, other role, value 2 | special control `0x57A816(0)` |
| Type0, other role, other ≠0 | set `0x2007502E`=1, counter `0x20074A9C`=0, DSP enable |
| Type0, other role, 0 | clear both, watchdog stop, I2S stop `0x57A734`; inactive I2S → `osDelay(50)` |
| Type1 | primary PDM only if role==1 and variant==0, else alternate; ≠0 → enable `0x57B4A8` / `0x57B770`; 0 → clear active marker then PDM IRQ clear `0x5925B4(handle,0x18)` |

Emitters: `0x53CA10(v)` posts `{0,1,(u8)v}`; `audio_pdm_control 0x53CA32(v)` posts `{1,1,(u8)v}`. (pre-consolidation:g2/analysis/audio-source-candidate-20261010/REPORT.md)

### 1.3 Watchdog timer

- Timer handle `0x20074A98`; start `0x53C2BE` = `osTimerStart(2000 ticks)` + logging; stop `0x53C31C`.
- Callback `0x53C2A4` **ignores its argument**, posts `{6,0,0}`.
- Type-6 handler `0x53C92E`: if enable byte `0x2007502E`≠0, snapshot-and-clear consumed-PCM counter `0x20074A9C`; if prior count <20 emit `{0,1,2}` (DSP restart path). Threshold is a count of PCM consumptions, not ms.
(pre-consolidation:g2/analysis/audio-watchdog-callback-closure-2026-10-09/REPORT.md; audio-source-candidate-20261010/REPORT.md)

### 1.4 Stop handshake and exit

- Thread manager `0x4C96B6`/`0x4C95BC` sends thread flag **0x800000** to each worker; worker acknowledges by `0x4C9C3C(i)` = `osEventFlagsSet(group@0x200040F4, 1<<(u8)i)` (group from `0x200040D8+0x1C`). Audio ack = event **0x08**.
- `AUD_ThreadExit 0x53CDC2` order: **ack first**, then stop/delete timer `0x20074A98`, delete queue `0x20003FA4` (handles cleared even if delete fails, e.g. −6 in ISR), then `osDelay(0xFFFFFFFF)` forever. Ack is not a cleanup/quiescence fence; no DMA disable in this path.
- Single stop `0x4C95BC` waits `osEventFlagsWait(...,WaitAll,20000 ticks)`; coordinator `0x4C9778` waits accumulated mask, `5000 ticks`, logs mismatch, continues.

| Context base | Ack bit | | Context base | Ack bit |
|---|---|---|---|---|
| `0x200040FC` | 0x02 | | `0x20003F98` (audio) | 0x08 |
| `0x20004120` | 0x40 | | `0x2000408C` | 0x10 |
| `0x20004044` | 0x800 | | `0x20003664` | 0x20 |
| `0x20003FFC` | 0x80 | | `0x20000658` | 0x1000 |
| `0x20004020` | 0x100 | | `0x20004068` | 0x200 |

Fanout ignores setter errors and includes null-handle bits; reason bit5 skips `0x20003FFC/4020/4068` (mask `0x187A` vs `0x1BFA`).
(pre-consolidation:g2/analysis/audio-stop-handshake-closure-2026-10-08/REPORT.md; pre-consolidation:g2/analysis/audio-exit-cleanup-closure-2026-10-08/REPORT.md)

### 1.5 Diagnostic codec/PDM deinit

- `0x58F74A` (mode 0, codec) / `0x58F806` (mode 1, PDM): **queue disable control first** (`{type=mode,1,0}`, sets flag 0x400000), then unregister owner `0x10B`; wrong owner returns −1 after disable was already queued.
- Then recording stop: recorder rows at `0x20073C08 + 12*mode` (`+0` file ptr, `+10` active byte) → `file_close 0x4745F4`, then LC3 setup of diagnostic configs (§3).
(pre-consolidation:g2/analysis/audio-diagnostic-deinit-closure-2026-10-08/REPORT.md)

---

## 2. I2S DMA, PCM hand-off and consumers

### 2.1 I2S interrupt and two-stage DMA

- Vector `0x4380F0` → ISR `0x57A4D8` (IRQ **44**, word `0x78F558`). ISR captures enabled status, INTCLR + readback, calls service `0x5908A0`, then if captured **bit 4** (RX complete) calls notifier `0x53C6B2` — it **ignores service return 9 (busy)**.
- Service helpers: DMA error `0x590CF4`, IPB `0x5909B6`, clear `0x590818`, status `0x590848`.
- Registers (pinned Ambiq header + offsetof check): `+0x224/+0x220/+0x21C` = **RX NEXT address / count / enable** (next job, not current); TX `+0x22C/+0x228`, next-enable bit 1.
- Service: errors zero DMACFG + status (no re-enable); RX handled before TX; each clears completion **before** busy test; busy → 9 without toggling (RX success persists if TX busy — not atomic). Otherwise ping/pong toggle, writes slot, next address, count = `byte_len>>2`, ORs enable.
(pre-consolidation:g2/analysis/audio-dma-rearm-2026-10-06/REPORT.md)

### 2.2 Cache hand-off getter

- `0x57A7E0`: handle ptr `*0x2007450C` → channel0 selected-buffer query `0x590B6C`, D-cache invalidate of **3,200 B** (flag 0), publish address + 3200, return address. Borrowed buffer: no copy/refcount/lock/release. Length is constant regardless of DMA count field.
(pre-consolidation:g2/analysis/audio-cache-handoff-2026-10-06/REPORT.md; audio-dma-rearm-2026-10-06/REPORT.md)

### 2.3 Notification → consumer

| Stage | Behaviour |
|---|---|
| Notifier `0x53C6B2` | builds `{type=2, 0, tick=osKernelGetTickCount()}` |
| `0x53C638` / ISR put `0x449ABE` | copy into queue; full → resource error; success → flags 0x400000 |
| Task get `0x449B3C`/`0x441B0A` | FIFO copy-out, zero wait |
| Consumer `0x53C6F2` | `now - tick` (u32 modular); accept **0..40 ticks**, ≥41 → log & drop; then getter `0x57A7E0`, forward to `0x57ADF8`; increments `0x20074A9C` |
| PCM dispatch `0x57ADF8` | u8 mode; guards mode≥2/null/zero; rows at `0x20073C20` (12 B: owner `+0`, mode `+4`, callback `+8`, callback reread before BLX); missing mode-0 registration → DSP fallback, mode 1 returns |

The message carries no buffer identity, so a "fresh" timestamp does not identify the DMA period consumed.
(pre-consolidation:g2/analysis/audio-notification-pcm-2026-10-06/REPORT.md; audio-dma-rearm-2026-10-06/REPORT.md)

### 2.4 PCM callback registry (audio)

- Register `0x57AB78`: overwrites occupied row (no exclusivity); clears row, stores owner, mode, callback **last**.
- Unregister `0x57ACD0`: checks callback then owner; **no mode<2 check** (mode 2 addresses next row; 256 aliases 0); wrong owner cannot remove; empty row returns success without clearing stale fields.
- Only direct callers: codec/PDM production initializers, owner `0x10B`; codec mode0 callbacks `0x58F5E1`/`0x58F4E5`, PDM mode1 `0x58F5E1`; these reach `0x57B1F4` and `file_write 0x474682` (not the BLE notify path); option byte `0x20004551` selects raw PCM vs encode-to-stack.
(pre-consolidation:g2/analysis/audio-registration-2026-10-06/REPORT.md)

### 2.5 I2S HAL (Ambiq `am_hal_i2s`, stock bodies)

| Function | Facts |
|---|---|
| DMA stop `0x590C62` | reads handle+4 **before** NULL check; tag `handle[0]&0x1FFFFFF == 0x01125125` else 2; bit25 clear → 0; releases clock group 4 (`0x4C4530(4, 29+module)`); if `+0x60` active: clear ctrl bits 0,12 at `0x40208100+module*0x1000`, reconfig `0x58FDBC(module,0x217)`, release source group mapped by `0x58FD1C(handle+0x5C)`; clears bit25 |
| Power `0x590648(h,mode,backup)` | mode 0 on/restore, 1/2 off/save, else 6; restore w/o snapshot → 7; snapshot regs at `h+0x0C..+0x38` = offsets `{0x48(&0x11),0x40,0x44,0x54,0x100,0x4C,0x10,0x30,0x300,0x200,0x60,0x64}` of `0x40208000+module*0x1000`; snapshot marker `h+8`; peripheral on/off returns ignored |
| Uninit `0x5900CE` | NULL-safe; clears marker bit24, module word; does not clear bit25/free/poll |
| Reconfig `0x58FDBC` | request `0x217` = enable byte0, source byte2, divider 23; sets ctrl bits16..18=4, divider bits4..8 |
| Clock source `0x58FD1C` | 98-B selector, reads `0x40004048` bit30 |
| Power descriptors | module0 idx31 `{0x4002100C,0x40,0x40021010,0xC0}`, module1 idx32 cmd mask 0x80 |
| Stop `0x57A734` | active byte `0x20074FB7` cleared **first**, NVIC disable IRQ44 (`0xE000E184=0x1000`) via `0x57A48A`, then clock-stop `0x4C3138(0,0)` |
| Clock group 4 | clients `0x20073344` (2 words), peripheral 29/30; last client → `0x4D391E(0)` (HFRC force bit0 at `0x40004044`), no status poll |

PDM: primary active `0x20074FBB`/handle `0x20074550`; alternate `0x20074FBA`/`0x2007454C`; IRQ clear `0x5925B4` tag `0x01F956E2`, writes `0x40201000+inst*0x1000+0x108`, reads `+0x104`. NVIC disable `0x57A48A` writes `1<<(irq&31)` to ICER (`0xE000E180`) for non-negative s16 IRQ.
(pre-consolidation:g2/analysis/audio-i2s-stop-closure-2026-10-08/REPORT.md; pre-consolidation:g2/analysis/audio-i2s-power-closure-2026-10-08/REPORT.md; pre-consolidation:g2/analysis/audio-i2s-clock-release-closure-2026-10-08/REPORT.md; audio-control-callbacks-closure-2026-10-08/REPORT.md; audio-source-candidate-20261010/REPORT.md)

Other entry addresses: I2S enable `0x57A65C`, PDM enable primary `0x57B4A8` / alternate `0x57B770`, special control `0x57A816` (two delays + logger). (audio-source-candidate-20261010/REPORT.md)

---

## 3. LC3 encoder setup (liblc3-compatible)

- Wrapper `0x57A926(cfg)`: always reinitializes non-NULL cfg: `setup 0x591374(cfg+4 duration, cfg+8 rate, pcm_rate 0, workspace cfg+28)` → pointer stored at `cfg+24`. Invalid → NULL stored. No alloc/free.
- Duration helper `0x590D3C`: 2500/5000/7500/10000 → 0..3. Rate helper `0x590D74`: 8k/16k/24k/32k/48k → 0..4; hi-res mode accepts 48k/96k → 5/6 and rejects 7500 µs. Stock wrapper uses hi-res 0.
- Geometry table `0x7728D4` = `{20,40,60,80,120,120,240}`. Workspace: `+0/+1/+2` duration/codec-rate/pcm-rate index bytes; `+0x4A0..+0x4A8` derived offsets; history zeroed from `+0x4AC`; `history_bytes = 4*(ns + (nd+ns)/2 + ns/2 + lookback)` with `ns=rate*dur/1e6`, `nd=rate*1250/1e6`, `lookback=rate*(dur==7500?2000:1250)/1e6`. For 10 ms/16 kHz: indices `{3,1,1}`, history 1400 B, init span ends at workspace+2596 (2624 incl. 28-B prefix; stock config spacing 2628).
- Diagnostic encoder configs (from startup record `0x75D404`), 7 words `{fmt, duration, rate, ch_stride, ch_sel, bitrate, encoder*}`: `0x20106A7C {0,10000,16000,2,0,32000,0}`, `0x201074C0 {0,10000,16000,2,1,32000,0}`, `0x20107F04 {0,10000,16000,1,0,32000,0}`. Distinct from mono BLE record `0x20108948`.
(pre-consolidation:g2/analysis/audio-encoder-setup-closure-2026-10-08/REPORT.md; audio-diagnostic-deinit-closure-2026-10-08/REPORT.md)

---

## 4. DSP direction/angle helpers and DSP control

| Entry | Size | Facts |
|---|---:|---|
| `0x59188E` clamp | 34 | D0 value, D1 lo, D2 hi; uses `VCMP.F64` (non-signalling; GCC's `VCMPE` differs on quiet-NaN IOC) |
| `0x5918B0` delay→angle | 28 | `asin(clamp(D0*D2/D1, -1, +1))` |
| `0x5918CC` correlation | 728 | r0/r1 int16 L/R, r2 count, r3 lag limit (default 8), d0..d4 = sample rate, mic spacing, speed of sound, RMS floor, quality floor; 4 optional stack output ptrs; signed-64 dot products, strict-greater tie, mean-abs quality; quiet NaN `0x7FF8000000000000` (built at `0x59187A`) |
| `0x591BA4` | 88 | fixed 800-sample angle wrapper |
| `0x59C7AC` | 84 | integer-only signed64→double (r0:r1 in/out) |
| `0x59C800` | 28 | sqrt: `VCMPE`+`VSQRT.F64`; negative → high word `0x7FFFFFFF`, tail to domain-error `0x439CA4` (errno **33** at `0x20074F14`) |
| `0x43C260` asin | 254 (+16 lit) | IAR DLIB-family double asin; table near `0x43C370`; `asin(±2)` → errno 33, returns `0x7FFFFFFF00000000`; host libm matches 156/246 finite inputs, newlib `__ieee754_asin` 0/768 full-state — **not newlib** |

DSP control wrappers: `audio_dsp_enable 0x57D6B4`, `disable 0x57D794`, `gate 0x57D93C`, 200-tick timeout, return status or −1.
DMIC request `0x57CE78` (388 B) opcode **12/13** (open/close); I2S-output request `0x57D024` (380 B) opcode **15** with 1-byte payload; both: family `0x100`, up to 3 attempts, zeroed 26-B transaction descriptor (`+14` response ptr, `+18` u16 response length), send `0x57C512`, release `0x57C640` (frees via file heap `0x474D16`, then 32-bit zero at `+14`, 16-bit zero at `+18`).
(pre-consolidation:g2/analysis/audio-dsp-frontier-20261010/REPORT.md; audio-source-candidate-20261010/REPORT.md)

---

## 5. GX8002 codec control link (UART3, `BUXX`)

Wire framing summary is in [protocols.md §8](protocols.md); details below are new.

### 5.1 Request/transmit path

- Chain: pack `0x57BB0A` → send `0x57C0D6` (shared buffer `0x2007399C`) → codec TX `0x58FB38` → channel TX `0x55E7FA` → HAL type-0 blocking `0x58E3F8`/`0x58E454`.
- Command field = `(lowArg & 0xFF) | (highArg & 0xFF00)`. Sequence byte `0x20075013` increments (u8 wrap) even if later TX fails.
- Any non-zero CRC flag → wire flag 1 and length +4. Gate: adjusted wire-body ≤16 → max payload 16 (no CRC) / 12 (CRC). Pack returns −1 NULL, −2 too long; u16 length wraps (65532+CRC → 0 passes gate).
- Quirks: NULL payload with nonzero length leaves stale buffer bytes; zero payload with CRC flag declares 4 but writes no trailer.
- Channel TX polls completion marker up to 1000×`delay(10)` even after HAL error; marker absence does not fail a successful HAL return. Channel 3 has a 1024-B software TX queue at `0x200BA420` so buffer reuse after blocking admission is safe.
(pre-consolidation:g2/analysis/audio-codec-request-tx-2026-10-09/REPORT.md; pre-consolidation:g2/analysis/audio-uart3-tx-irq-drain-2026-10-09/REPORT.md)

### 5.2 Response path

- send/wait `0x57C512` → read wrapper `0x57C442` → blocking reader `0x57C1FC` → codec UART read `0x58FB2A` (returns drained count). On read success the caller runs cleanup `0x57BAEC` **before** unpack `0x57BD06`. Neither reader validates magic/CRC; send/wait does not match response command/seq to request.
- CRC: `0x58FAAC` → `0x4D34C4` (NULL prior state); table `0x699BA8` = standard reflected `0xEDB88320` zlib CRC-32 (`"123456789"` → `CBF43926`).
- Unpack: copies 14 header bytes to output **before** validation; u16 total; header CRC before allocation; payload allocated exactly, ptr `+14`, len `+18`, trailer `+20`, total `+24`. Returns −1 bad input/short, −2 magic, −3 short frame, −4 header CRC, −5 payload>16, −6 alloc, −7 body CRC (frees, ptr zeroed, length kept).
- **Bug/quirk:** CRC-flagged empty payload (wire length 4) skips trailer verification entirely.
- Reader writes 14 bytes before checking caller capacity; declared 65535 wraps total to 13. Header and body share one deadline: u64 elapsed = now − start compared to u32 timeout; timeout 0 rejects staged bytes.
- Other `0x58FB2A` callers: one-byte helper `0x58FAD2`, `0x579CBC`, `0x57C1FC`; MicDelay1Bit `0x57D1CC`, GetVoiceEvent `0x57DA40` use send/wait.
(pre-consolidation:g2/analysis/audio-codec-response-crc-2026-10-09/REPORT.md; pre-consolidation:g2/analysis/audio-codec-uart-rx-drain-2026-10-09/REPORT.md; pre-consolidation:g2/analysis/audio-transition-snapshot-successor-2026-10-09/REPORT.md)

### 5.3 Timing arithmetic

- Tick wrapper `0x58FAC8` = `osKernelGetTickCount 0x4490CC` zero-extended to u64 (both ISR/task branches read `0x20074A34`).
- One-byte reader `0x58FAD2`: deadline = u64 start + **sign-extended** timeout, checked **before** reading; reached → `0xFFFFFFFF`; failed read → `osDelay(1)`. Near-wrap starts (e.g. `0xFFFFFFFE`+5) produce a deadline never reached by a 32-bit tick; timeouts ≥`0x80000000` behave as negative.
(pre-consolidation:g2/analysis/audio-codec-uart-deadline-2026-10-09/REPORT.md)

### 5.4 UART3 lifecycle and RX ring

| Item | Value |
|---|---|
| Init `0x58FB52` | guarded by initialized byte `0x20075014`: ring setup `0x598160(0x20073ED4, storage 0x200731B0, 64)`, install callback `0x58FB1D` on channel 3, then channel enable `0x55E5BC` gated by open byte `0x20075015` |
| Close `0x58FC0C` | channel disable `0x55E630`; clears open only on success; **never resets initialized, ring or callback** — buffered bytes survive close/reopen |
| Ring | 64 B, mask 63 (63 usable); callback `0x58FB1C` → byte write `0x5981C4` (put `0x598198`, full `0x598146`); **full put evicts oldest byte**; empty `0x598134`, get `0x5981E0`, bounded read `0x59820A` |
| Host init `0x57BA88` | requests **115200** baud (`0x58FAB6` → `0x55E898`) and **ignores** the baud error |
| IRQ wrapper `0x55E2CE` | status → clear → HAL service; bit `0x10` read ≤15 B accumulate; bit `0x40` read ≤16 B, callback(staging, count), reset count; bit `0x01` sets completion `+25`; RX object count `+8`, staging ptr `+12` |

**Bug:** close clears channel-active `+24` before HAL validation; HAL invalid-handle (2) → codec close −1 with open byte still 1; next host init skips enable, ignores baud failure and returns 0 (state initialized=1, open=1, active=0). Failed enable likewise leaves channel-active=1 with open=0 (no rollback). HAL power ignores peripheral/clock provider failures.
(pre-consolidation:g2/analysis/audio-codec-uart-lifecycle-2026-10-09/REPORT.md; pre-consolidation:g2/analysis/audio-codec-lifecycle-hal-composition-2026-10-09/REPORT.md; pre-consolidation:g2/analysis/audio-codec-uart-irq-delivery-2026-10-09/REPORT.md; pre-consolidation:g2/analysis/audio-uart-rx-consumer-2026-10-09/REPORT.md)

### 5.5 UART HAL interrupt/FIFO bodies used by the codec

- `codec_irq_service 0x58E860` = `am_hal_uart_interrupt_service` with a **stock difference: clears busy byte `handle+0x11B` at the end of every active service** (pinned SDK clears it only in specific helpers; stock DMA helpers `0x58DD30`/`0x58DD5C` do not). Active branch: count ptr `+0xE8`, status bits 6/12/11, stored callback `+0xF0` with arg `+0xF4`; COUNT uses 12-bit TOTCOUNT. Inactive: read mask `0x50`, TX `0x20` (→ TX SM `0x58E534`), TXCMP `0x1` sets `+0xDE`. Helpers: DMA complete `0x58DD30`, DMA abort `0x58DD5C`, error lookup `0x58DD8A`, RX abort `0x58DFEE`, RX read SM `0x58E618`.
- `codec_fifo_read 0x58E2D8`, `codec_irq_clear 0x58E7E4`, `codec_irq_status 0x58E80E`: instance at `handle+0x28` read **before** NULL/tag check; tag `0x01EA9E06`; UART base `0x40039000 + inst*0x1000` (UART3 = `0x4003C000`), clear `+0x44`/read `+0x40`, status raw `+0x40` / masked `+0x3C`, RX status `+0x18`, data error bits 8–11.
(audio-source-candidate-20261010/REPORT.md)

---

## 6. Apollo UART HAL and UART consumers

### 6.1 HAL (`am_hal_uart`, SDK 5.1.0 bodies, revision text `release_sdk5p1p0-366b80e084`)

| Body | Address |
|---|---|
| tx save | `0x58DEF2` |
| blocking / nonblocking write | `0x58E454` / `0x58E4E8` |
| TX state machine | `0x58E534` (queue add `0x530084`, get `0x5300E2`) |
| power control / configure / baud | `0x58DBB8` / `0x58E09E` / `0x58DE38` |
| transfer (type routing) | `0x58E3F8` |

Layouts: transfer 56 B (`src+0, count+4, out+8, timeout+12, cb+16, ctx+20, type+52`); UART state 284 B stride at `0x2006A02C` (`module+40, txqueue+52, activeTX+160, written+216, queue_enabled+220, last_tx_complete+222, writing+281`); queue 24 B (`wr+0, rd+4, len+8, cap+12, itemsize+16, data+20`).
Semantics: blocking success means bytes consumed into FIFO/queue, not transmitted; nonblocking partial return keeps a borrow on remaining bytes; **timeout 0 is not immediate** (counter compared after increment). Baud helper reports integer rate (921600 → 923076; >1,500,000 selects 48 MHz); SYSPLL source rejected on revision `0x21`. Stock interrupt-clear writes IEC `0x40039044` then reads MIS `0x40039040` (earlier "extra read" claim was wrong).
(pre-consolidation:g2/analysis/audio-uart-tx-ownership-2026-10-09/REPORT.md; pre-consolidation:g2/analysis/audio-uart-tx-ownership-2026-10-09/pseudocode.md; pre-consolidation:g2/analysis/audio-uart-power-config-2026-10-09/REPORT.md; pre-consolidation:g2/analysis/audio-uart-group-power-2026-10-09/REPORT.md)

### 6.2 Channel table and logger UART (channel 1)

- Channel records `0x20000D2C`, stride 28: `+4` HAL handle, `+8` pin table, `+12` config, `+16` queue descriptor, `+20` RX callback, `+24` active, `+25` completion. Enable `0x55E5BC` sets active even if power failed; disable `0x55E630` clears active first, writes shutdown pad words (RX3/TX `0xE083`). Init `0x55E388` configures channels 1–3 then shuts them; `0x5093AC` later enables channel 1.
- Channel 1 (logger): module 1, pins `0x786060` (logical 12/14, cfg 5), config `0x20000CCC` = **921600 8N1, HFRC**, no TX queue; RX staging `0x200B9C20`, descriptor `0x20000CFC` (`+8` staged count). RX callback `0x5415E6` → `xStreamBufferSendFromISR(*0x200748BC, …)` and **discards accepted count** (staging reset → rejected suffix lost).
- Logger stream: created by `0x54171C` (2048 usable, trigger 1, stream mode) via `0x57DEEA` = one 2085-B allocation (36-B control + 2049 storage). Stream control: `tail+0, head+4, len+8, trigger+12, waitRecv+16, waitSend+20, buf+24, flags+28, trace+32`.
- Log sink: setter `0x472C7C` stores the callback at `0x200742F0`. Installer `0x54171C` (called from `0x4C953E` before `uart_instance_init 0x541A2E`) installs `0x5415C3`, which `strlen`s and writes channel 1 blocking. Ghidra marked `0x54171C` undecompiled; a raw BL scan found this real installer (census labels are incomplete).
- Disable path `0x4C2B30` (chain `0x5CDD14→0x4C2AE8→0x4C2B30`): clears the sink only if flag `0x20074F4E`==1 and `0x539254` (clears ITM_TCR `0xE0000E80` SWOENA/ITMENA) and `0x539304` (trace refcount byte `0x20074F7E`, clock release) both return 0; then pin 0x1C → config `*0x78EE3C` (logical 28/raw 3). Sink and flag both start zero (BSS); no later writer of the flag found.
(pre-consolidation:g2/analysis/audio-uart-tx-ownership-2026-10-09/REPORT.md; pre-consolidation:g2/analysis/audio-uart-rx-stream-ownership-2026-10-09/REPORT.md; pre-consolidation:g2/analysis/audio-uart-rx-stream-ownership-2026-10-09/pseudocode.md; pre-consolidation:g2/analysis/audio-logger-stock-provider-closure-2026-10-09/REPORT.md; pre-consolidation:g2/analysis/audio-logger-disable-path-2026-10-09/REPORT.md; pre-consolidation:g2/analysis/audio-logger-provider-composition-2026-10-09/REPORT.md)

### 6.3 Temple-sync worker

- `uart_instance_init 0x541A2E`: `osThreadNew(0x5417D7, NULL, attr 0x75C1EC)` → handle `0x20074B0C`; name `uart_sync_thread` (`0x7846A8`), CB `0x20072530`/112 B, stack `0x20370E40`/4096 B, priority **42**; failure logs `[sync.module.uart]Failed to create uart sync thread`.
- Task `0x5417D6`: event bit1 drains ≤32×1024 B from 24,576-B stream at `0x20074B14` into `0x2006C930`, parser `0x45D4DC`; product-mode reads 10 B; sync callback `0x5417A4` ISR-sends and sets bit1. UART3 is **not** routed to this stream (codec only).
(pre-consolidation:g2/analysis/audio-uart-instance-closure-2026-10-09/REPORT.md; audio-uart-rx-consumer-2026-10-09/REPORT.md; audio-codec-uart-rx-drain-2026-10-09/REPORT.md)

### 6.4 Formatters and loggers

- Text formatter `0x473036` = Ambiq `am_util_stdio` from **`release_sdk_3_2_0-dd5f40c14b`** (same as bootloader adaptation): subset of printf; `%-8s` appends 8 spaces after the string (non-standard width); LF→CRLF; 64-bit args 8-aligned; `%f` via `VCVT.F32.F64` at `0x473392`; no destination capacity.
- Short binary logger `audio_log_simple 0x43CE9E` (5,718 call sites; 4,523 distinct resolved format strings): policy byte `0x20074FA1` (getter `0x44A9AE`), lock state ptr `0x20074388`, recursive lock `0x441750` (500 ticks)/unlock `0x441710`, token = mask high 10 bits | fmt low 22 bits; formatter `0x43CB84` (794 B) emits a **binary packet ≤44 B** (header: seq byte `0x20074F9F`, tick mod 1000, context, token+count; ≤32-B payload; `%s` 16-B tail; `%f` FP64→FP32; unknown `ll` conversions consume an unaligned word).
- Output `0x43CA50(packet,len)`: ring descriptor `0x200004C8` = `{base 0x200CCBD8, cap 0x8000, rd, wr}` (stock init), one slot reserved, 16-bit length, flush thresholds 236/4096 B; drain `0x43D040`.
- Extended variadic logger `0x43D574` (1,026 B) is separate and unresolved. Log flags byte `0x20004543` (getter `0x43D0CE`), level `0x43D0DA`.
(pre-consolidation:g2/analysis/audio-main-formatter-source-successor-2026-10-09/REPORT.md; audio-dsp-frontier-20261010/REPORT.md)

---

## 7. FreeRTOS / CMSIS-RTOS2 internals (V10.5.1, stock addresses)

### 7.1 Kernel globals and layouts

| Global | Address | | Global | Address |
|---|---|---|---|---|
| `pxCurrentTCB` | `0x20074A20` | | pending ticks | `0x20074A40` |
| delayed list ptr / overflow ptr | `0x20074A24` / `0x20074A28` | | yield pending | `0x20074A44` |
| task count | `0x20074A30` | | overflow count | `0x20074A48` |
| tick count | `0x20074A34` | | next unblock | `0x20074A50` |
| top ready priority | `0x20074A38` | | scheduler suspended | `0x20074A58` |
| scheduler running | `0x20074A3C` | | ready lists | `0x2006A49C + 20*prio` |
| pending-ready list | `0x20073D24` | | suspended list | `0x20073D4C` |
| critical nesting | `0x2000309C` | | switch history ring | `0x2006F348` (64 pairs), index `0x20074A5C` |

TCB (112 B): `+0` top of stack, `+4` state item, `+0x18` event item, `+0x28` event container, `+0x2C` priority, `+0x30` stack base (4× `0xA5A5A5A5` canary check), `+0x58` value logged into the switch-history ring (G2 trace hook; not vanilla), `+0x68` notification value, `+0x6C` notify state (0 none, 1 waiting, 2 received). List item 20 B (`value, next, prev, owner, container`); list 20 B (`count, index, sentinel`). Queue: senders `+16`, receivers `+36`, count `+0x38`, length `+0x3C`, item size `+0x40`, RX lock `+0x44`, TX lock `+0x45`, static marker `+0x46`.
(pre-consolidation:g2/analysis/audio-timer-wake-provider-closure-2026-10-08/pseudocode.md; pre-consolidation:g2/analysis/audio-uart-rx-notifier-2026-10-09/pseudocode.md; pre-consolidation:g2/analysis/audio-pendsv-closure-2026-10-08/REPORT.md; pre-consolidation:g2/analysis/audio-queue-delete-closure-2026-10-08/REPORT.md; pre-consolidation:g2/analysis/audio-notification-wake-closure-2026-10-08/REPORT.md)

### 7.2 Function map

| Kernel | Addr | | Kernel | Addr |
|---|---|---|---|---|
| `xTaskGetTickCount` | `0x454EFE` | | `xTaskGetCurrentTaskHandle` | `0x45589C` |
| `vTaskSuspendAll` | `0x454D7C` | | `xTaskResumeAll` | `0x454DCC` |
| `xTaskIncrementTick` | `0x45504C` | | `vTaskDelay` | `0x454B4C` |
| `vTaskSwitchContext` | `0x4551B4` | | PendSV handler (vector `0x438038`) | `0x5FA0C8` |
| `portYIELD` (ICSR `0x10000000`) | `0x4420BC` | | enter / exit critical | `0x4420D0` / `0x4420E8` |
| BASEPRI save / restore | `0x5FA0A4` / `0x5FA0BA` | | PRIMASK save (`mrs;cpsid;bx`) | `0x473940` |
| `xTaskNotifyWait` | `0x455B84` | | add current to delayed list | `0x455FA8` |
| `xTaskGenericNotify` / FromISR | `0x455C48` / `0x455DC0` | | `xTaskRemoveFromEventList` | `0x455370` |
| `prvUnlockQueue` | `0x441F88` | | `vQueueWaitForMessageRestricted` | `0x442030` |
| `vListInsert` / `uxListRemove` | `0x4560B2` / `0x4560E8` | | reset next unblock | `0x455876` |
| priority inherit / disinherit / timeout-disinherit | `0x4558CC` / `0x45596E` / `0x455A1C` | | mutex held++ | `0x455AE0` |
| `xQueueSemaphoreTake` | `0x441C44` | | highest waiter prio | `0x441EC4` |
| recursive give / take | `0x441710` / `0x441750` | | `xQueueReceive` | `0x441B0A` |
| receive / give FromISR | `0x441DA6` / `0x441A42` | | send task / ISR | `0x4417EE` / `0x441952` |
| queue create static / dynamic | `0x441696` / `0x441636` | | `vQueueDelete` | `0x441EA2` |
| static task create / init / add ready | `0x454820` / `0x454938` / `0x4549FC` | | task delete / state | `0x454AAE` / `0x454B88` |
| `pvPortMalloc` / `vPortFree` | `0x456110` / `0x456210` | | malloc-failed / stack-overflow hook | `0x46D85E` / `0x46D86C` |
| notify state clear | `0x455F5E` | | fatal asserts (10-B `*(0xFFFFFFFF)=0; b .`) | `0x441800`, `0x45537E`, `0x4420F6` |

| CMSIS-RTOS2 | Addr | | CMSIS-RTOS2 | Addr |
|---|---|---|---|---|
| `IRQ_Context` | `0x44900E` | | `osKernelGetTickCount` | `0x4490CC` |
| `osThreadNew` / `Terminate` | `0x4490E2` / `0x4491FE` | | `osThreadFlagsSet` / `Wait` | `0x449238` / `0x4492C2` |
| `osDelay` | `0x449376` | | `osTimerNew` / callback adapter | `0x4493B0` / `0x449398` |
| `osTimerStart` / `Stop` / `Delete` | `0x449498` / `0x4494D8` / `0x44953E` | | `osEventFlagsSet` / `Wait` | `0x4495E4` / `0x44969C` |
| `osMutexAcquire` / `Release` | `0x4497B6` / `0x44981C` | | `osSemaphoreAcquire` / `Release` | `0x44994E` / `0x4499B8` |
| `osMessageQueueNew` / `Put` / `Get` / `Delete` | `0x449A32` / `0x449ABE` / `0x449B3C` / `0x449BEC` | | `osMemoryPoolAlloc` | `0x449D3E` |
| event groups: set / setFromISR / get / wait | `0x47ED76` / `0x47EE4A` / `0x47ED64` / `0x47EBF8` | | | |

(sources: pre-consolidation:g2/analysis/audio-source-candidate-20261010/REPORT.md and the per-topic reports cited in §7.3–7.6)

### 7.3 Scheduler behaviour notes

- Critical entry sets BASEPRI `0x30` exactly (not BASEPRI_MAX), increments nesting; exit clears BASEPRI at 0; zero-nesting exit → fatal `0x4420F6`.
- `vTaskSwitchContext`: if suspended sets yield-pending; else checks canary, logs outgoing/incoming `TCB+0x58` into history ring, scans from top priority.
- PendSV: pushes S16–S31 when EXC_RETURN bit4 clear, then 10-word frame `{PSPLIM, EXC_RETURN, R4–R11}`; ends `BX EXC_RETURN` at `0x5FA11E`.
- Yield rule differs by path: ISR notify / event unblock wake require **strictly higher** priority; final `xTaskResumeAll` (pending-ready drain) yields for **≥ current** priority.
- Resume order: pending-ready tasks moved **before** pending ticks replayed via `0x45504C`; tick expiry does **not** mark notifications received.
- `osThreadFlagsSet(t,0)` is not neutral: it sets notify state to 2; returned flags include all existing bits; flags are low 31 bits (bit31 → −4).
- Notify-wait: `NoClear` preserves bits but always resets the received marker; WaitAll with 0 is vacuous; WaitAny 0 never matches.
- `vTaskDelay`/`osDelay` composition (suspend → `0x455FA8` → resume → yield) not jointly validated.
(pre-consolidation:g2/analysis/audio-pendsv-closure-2026-10-08/REPORT.md; pre-consolidation:g2/analysis/audio-pending-resume-closure-2026-10-08/REPORT.md; pre-consolidation:g2/analysis/audio-resume-ticks-closure-2026-10-08/REPORT.md; pre-consolidation:g2/analysis/audio-tick-expiry-closure-2026-10-08/REPORT.md; audio-thread-flags-closure-2026-10-08/REPORT.md; pre-consolidation:g2/analysis/audio-notification-wait-closure-2026-10-08/REPORT.md; pre-consolidation:g2/analysis/audio-notification-block-insertion-2026-10-09/REPORT.md; pre-consolidation:g2/analysis/audio-notification-block-wake-return-2026-10-09/REPORT.md; pre-consolidation:g2/analysis/audio-notifier-resume-composition-2026-10-09/REPORT.md; pre-consolidation:g2/analysis/audio-notifier-tick-replay-composition-2026-10-09/REPORT.md; pre-consolidation:g2/analysis/audio-resume-yield-composition-2026-10-09/REPORT.md; pre-consolidation:g2/analysis/audio-delayed-block-closure-2026-10-08/REPORT.md)

### 7.4 Queues, mutexes, semaphores, pools

- CMSIS put ignores priority; ISR-style if IPSR≠0 or (scheduler running and PRIMASK/BASEPRI masked). Status map: −4 bad arg / ISR with timeout, −3 full/no-wait, −2 timeout, −6 ISR not allowed (mutex, delete). Handle bit0 = recursive mutex.
- CMSIS queue delete `0x449BEC` → `0x441EA2`: frees only if marker `+0x46`==0; no drain/destructor/waiter removal.
- Mutex: release decrements held count even without priority change; priority restored only at last mutex; timeout-disinherit leaves held count. Normal CMSIS release does not pre-check ownership (wrong owner → assert).
- Unlock services TX-lock receivers first, then RX-lock senders, signed-byte counts, publishes −1.
- CMSIS memory pool: 116-B control (36-B prefix + 80-B embedded semaphore), status `0x5EED0000|flags`; array bytes `count*((size+3)>>2)*4` but stride = raw size; LIFO free list in first 4 bytes of block; no alignment/double-free check; alloc failure after token taken does not refund.
(pre-consolidation:g2/analysis/audio-queue-cmsis-source-closure-2026-10-09/REPORT.md; audio-queue-delete-closure-2026-10-08/REPORT.md; pre-consolidation:g2/analysis/audio-mutex-disinherit-closure-2026-10-09/REPORT.md; pre-consolidation:g2/analysis/audio-semaphore-take-closure-2026-10-09/REPORT.md; pre-consolidation:g2/analysis/audio-semaphore-isr-closure-2026-10-09/REPORT.md; pre-consolidation:g2/analysis/audio-cmsis-memory-pool-closure-2026-10-09/pseudocode.md)

### 7.5 Heaps

- RTOS heap_4: 8-B header (`next+0`, `size+4`, bit31 allocated; size literal `0x78F118`), charge `n + 16 − (n&7)`, split only if remainder >16, address-ordered first fit, two-sided coalesce. Start sentinel `0x20074158`, end ptr `0x2007465C`, free bytes `0x20074660`, free count `0x2007466C`; fresh usable 192,504 B. Failure → hook, which self-loops (logger off) — exhaustion is fatal, not NULL.
- File heap is separate (TLSF): alloc `0x474CD2` / free `0x474D16` take mutex `0x200748F8` (1000 ticks), pool `*0x20074ABC`, TLSF malloc `0x4D0722` / free `0x4D0808` (create-with-pool `0x4D06EC`); failed acquire → logger `0x4733EE` + `0x4D09B4` (line 1086).
- `file_close 0x4745F4`: file mutex `0x200748F4` (1000 ticks) → backend `0x4CFAD0` (open-list check `0x4CB082`, sync `0x4CDF74`, unlink `0x4CB0A0` via `0x4CDCE4`) → release → wrapper free; returns 0/−1 after the free attempt.
(pre-consolidation:g2/analysis/audio-cmsis-memory-pool-closure-2026-10-09/REPORT.md; audio-timer-aux-lifetime-closure-2026-10-08/REPORT.md; audio-queue-delete-closure-2026-10-08/REPORT.md; pre-consolidation:g2/analysis/audio-file-close-closure-2026-10-08/REPORT.md; audio-source-candidate-20261010/REPORT.md)

### 7.6 Software timers and daemon

| Item | Value |
|---|---|
| Daemon task | entry `0x47E878` (20 B loop), created by `0x47E674` via static memory `0x4D3610`: TCB `0x20071EA0`, stack `0x2003FA98` 4096 words (16 KiB), priority **54**, name `0x78EBCC` |
| Command queue | `0x20074AB0`, 50 × 16 B, storage `0x2006D7B4`, control `0x20072EE8`; init `0x47EAB8`; list heads `0x20073D60/0x20073D74` via ptrs `0x20074AA8/0x20074AAC`; last sample time `0x20074AB8` |
| Loop | next expiry `0x47E8F2` → process-or-block `0x47E88C` → drain `0x47E97A` (278 B). **Due timers fire before queued commands are drained.** |
| Helpers | expired `0x47E83A`, sample time `0x47E916` (wrap → expire old list with now=`UINT32_MAX`, then switch `0x47EA90`), reload `0x47E812` / insert `0x47E93C`, command producer `0x47E7B0` (packet `{cmd,value,timer,woken}`; cmd<6 task send, ≥6 ISR send), active getter `0x47EAF6`, get ID `0x47EB26` |
| Timer object | 44 B: name+0, list item+4, period+0x18, ID+0x1C, callback+0x20, opaque+0x24, status+0x28 (bit0 active, bit1 static, bit2 autoreload); dynamic block 56 B |
| Commands | 3 stop, 4 start, 5 delete (daemon frees dynamic object); CMSIS stop returns resource error if inactive |
| CMSIS aux | `{callback, arg}` 8 B (min 24-B block); dynamic-ownership flag is **ID bit0**, independent of static timer bit; inline at `cbMem+44` when cbSize≥52 |

**Lifetime hazard (instruction-proven ordering, live reachability unproven):** `osTimerDelete 0x44953E` frees the dynamic aux immediately after enqueueing command 5, while the timer stays linked; a due timer processed before the drain calls adapter `0x449398` with freed (reusable) aux memory. Priority 54 daemon vs 47 audio sender: a higher-priority waiting receiver yields before the free.
(pre-consolidation:g2/analysis/audio-timer-daemon-closure-2026-10-08/REPORT.md; pre-consolidation:g2/analysis/audio-timer-daemon-order-closure-2026-10-08/REPORT.md; pre-consolidation:g2/analysis/audio-timer-commands-closure-2026-10-08/REPORT.md; audio-timer-aux-lifetime-closure-2026-10-08/REPORT.md; pre-consolidation:g2/analysis/audio-timer-delete-wake-closure-2026-10-08/REPORT.md; pre-consolidation:g2/analysis/audio-timer-wrap-closure-2026-10-08/REPORT.md; pre-consolidation:g2/analysis/audio-timer-queue-wait-closure-2026-10-08/REPORT.md; pre-consolidation:g2/analysis/audio-timer-yield-boundary-successor-2026-10-08/REPORT.md; audio-source-candidate-20261010/REPORT.md)

---

## 8. Clock manager (`am_hal_clkmgr`, SDK 5.1.0 family)

### 8.1 Ownership model

- User bitmap `0x20073324`: 7 clocks × 2 words (idempotent bits, not counts); users <57. Clocks: 0 LFRC, 1 XTAL-LS, 2 XTAL-HS, 3 external ref, 4 HFRC, 5 HFRC2, 6 SYSPLL. Known users: 52 CLKOUT (bit20 of `0x20073338`), 53 SYSPLL ref dependency, 54 HFRC2 ref dependency; group 4 clients at `0x20073344` (I2S peripherals 29/30).
- Public request `0x4C44BC` / release `0x4C4530`: narrow clock/user to u8 (256→0), user≥57 → 6, unknown clock → 6.
- LFRC `0x4C3BFC/0x4C3C2E`; XTAL-LS `0x4C3C60/0x4C3CA2` (reads LS Hz `0x200001D8` **before** checking ownership; SDK EXT32K enable/disable bodies absent); external ref `0x4C3CD4` (needs ext Hz; GPIO15 func 10 on acquire, 3 on last release — constants `0x78EE34/38`); XTAL-HS request `0x4C3D9E`, wait `0x4C3D70`, counter wait `0x4C387E` (150×`delay(10)`, success on exhaustion — no hardware poll). XTAL status `0x480C56` reads ctrl bit8/bit0 only.
- Board info: setter `0x4C45E2` copies 20 B to `0x200001CC` (no validation; SDK struct is larger); defaults from `0x77D8F8` (platform block `0x4C2B06`): **XTAL-HS mode 0 / 0 Hz, XTAL-LS 32768, external 12 MHz** → XTAL-HS request returns 7 at stock defaults.
- Config dispatcher (selector u8): 4 HFRC (`0x4C38A0`), 5 HFRC2, 6 SYSPLL, else 7.
(pre-consolidation:g2/analysis/audio-clock-manager-ownership-2026-10-08/REPORT.md; pre-consolidation:g2/analysis/audio-clock-public-dispatch-closure-2026-10-08/REPORT.md; pre-consolidation:g2/analysis/audio-xtal-request-closure-2026-10-08/REPORT.md; pre-consolidation:g2/analysis/audio-clock-leaf-providers-2026-10-08/REPORT.md; pre-consolidation:g2/analysis/audio-clock-driver-config-2026-10-08/REPORT.md)

### 8.2 Oscillators, registers and leaf providers

| Provider | Addr | Register behaviour |
|---|---|---|
| HFRC force | `0x4D391E` | `0x40004044` bit0 (u8 bool) |
| HFADJ apply / disable | `0x4D3938` / `0x4D3944` | packed config \| 1 / clear bit0 |
| HFRC2 force | `0x4D3952` | bit5; first set waits `0x40004030` bit24 (100 polls) |
| HF2ADJ apply | — | `0x4000404C`\|=7; ref bit → `0x40004048` b29; divider/ratio → `0x40004050`; enable bit0 |
| HFRC target / HFRC2 ratio | `0x4D3914` / `0x4D38EA` | int divide / `(ref>>div)` → float divide → Q15 (VFP fixed-point convert) |
| SYSPLL power on / off / query | `0x480058` / `0x48009E` / `0x4800E4` | chip major≥0x22: clear regulator `0x400201B0` b21 + delay; ctrl bits31/30; query = !bit31 |
| Oscillator ctl | `0x4809C4` | actions 0..6; action5 CLKOUT requests clock2/user52 **before** drive validation (drive 0,3..7) — invalid drive leaks the user; action3 overwrites trim, dropping SDK-preserved bits |
| HFRC config | `0x4C38A0` | only 0 (free-run ≈48 MHz) or 48 MHz adjusted; needs XTAL-LS; target into bits8..19 of `0x0025B800`; caches: Hz `0x20074250`, packed `0x20073F30`, valid `0x20004536`, stab flag/ptr `0x20074F57/0x20074264`, stabilized `0x20074F59` |

SYSPLL driver: init `0x5398E0` (ignores power-enable status), deinit `0x539944`, enable `0x539994` (needs SIMOBUCK status bits16..19), disable `0x539A10`, configure `0x539A40` (refdiv<64; feedback 4..960 integer / 10..96 fractional; postdiv<8, post1≥post2), lock wait `0x539B56` (polls `0x400204E4` bit0, timeout `ceil((VCO1?1875:1000)*refdiv/12)` µs). Generator `0x539794` calls min-VCO `0x539674` twice (60 MHz, 240 MHz), ≤50 postdivider via 50-B nibble table, VCO 60..960 MHz, PFD ≥10 MHz frac / ≥1 MHz int; PFD failure leaves partial writes. Example configs: auto SYSPLL 48 MHz from 12 MHz ext → `010101010501140000000000` (VCO 240 MHz); auto HFRC2 196.608 MHz → `010200009bc4200000000000`.
(audio-clock-leaf-providers-2026-10-08/REPORT.md; audio-clock-driver-config-2026-10-08/REPORT.md; pre-consolidation:g2/analysis/audio-syspll-generator-closure-2026-10-08/REPORT.md; pre-consolidation:g2/analysis/audio-info-memory-providers-2026-10-08/REPORT.md; audio-xtal-request-closure-2026-10-08/REPORT.md)

### 8.3 Ownership bugs/quirks in stock

- HFRC last-user release clears only force-on; **HFADJ and stabilized state are left set** (SDK disables them).
- HFRC2 adjusted-mode dependency failure: cleanup assigns the release return into the status, **overwriting the error** (returns 0 with caller bit clear, start-pending set).
- SYSPLL: only the selected reference's status gates progress; **lock-wait failure (4) leaves ownership, ref and enabled handle**; a repeat request returns 0 without re-checking lock. Release discards driver statuses.
- Repeated requests publish a stack-local counter pointer even when not stabilizing (stale pointer persists until last release).
- Manager accepts unsupported reference enum bytes (2/255); driver writes only bit0. Status query helpers skip bounds checks.
(pre-consolidation:g2/analysis/audio-hfrc-syspll-closure-2026-10-08/REPORT.md; audio-clock-manager-ownership-2026-10-08/REPORT.md; audio-clock-driver-config-2026-10-08/REPORT.md)

### 8.4 Timing primitives and float runtime

- `am_hal_delay_us 0x4807A0`: µs→float→u32 ×32 (5 fractional bits); if `0x40021000` bits3..4 == 2 count ×250/96 − 24, else −15; spins only if count>overhead, via ITCM `0x40` loop (decrement-then-branch; count 0 would underflow).
- Status waits `0x4807FC` / `0x480826`: poll **before** delay; compare `(reg&mask)` to **unmasked** expected; 5th arg u8 (≠0 equal, 0 not-equal; 256 inverts); budget N → N+1 reads, N delays, status 4.
- Float runtime (bespoke, no newlib/picolibc/SDK match): `floorf 0x43A5A0`, `roundf 0x577D08` (half away from zero), `ceilf 0x577D40` (bit manipulation, no FPSCR effect), `fmodf 0x577C3C` (integer remainder; x mod ±0 → `0x7FFFFFFF` + errno 33 via `0x577C34→0x439CA4`; x mod inf → x).
- Reset path enables CP10/CP11 at `0x5E4270`, writes **FPSCR `0x02040000`** at `0x5E4288` (DN bit25 set; bits18:16 = 4); no static FP-trap enable found.
(pre-consolidation:g2/analysis/audio-clock-timing-closure-2026-10-08/REPORT.md; pre-consolidation:g2/analysis/audio-float-runtime-closure-2026-10-08/REPORT.md; audio-dsp-frontier-20261010/REPORT.md)

---

## 9. Startup data, low-power init and power control

### 9.1 Scatter-loader records (table `0x75D3C8..0x75D410`, runner `0x5E42B4`, reset helper `0x5E4294`, reset vector `0x438004→0x5E4233`)

| Record | Action |
|---|---|
| `0x75D3CC` → zero routine `0x5FA01E` | zero `[0x20004558,0x20075048)` (461,552 B) and `[0x2013BE70,0x2037CE44)` |
| `0x75D3E4` → decoder `0x43A11E` | 22 B at `0x79430E` → 24 B ITCM `0x40..0x58`: `0x40` delay loop, `0x48` word copy (`do *d++=*s++; while(--n)`, returns src) — **not ROM** (earlier "missing resident ROM" was wrong) |
| `0x75D3F0/0x75D3F4` | 10,864 B at `0x79189E` → 17,752 B at `0x20000000` (ends at BSS `0x20004558`; SHA-256 `df1a1fdf…bb743`); contains dispatcher table `0x20003FBC`, logger ring descriptor, channel table |
| `0x75D404` | 8,615 B at `0x78F6F7` → `0x20080000..0x2013BE6E` (769,646 B, incl. 32 KiB zero logger ring, diagnostic LC3 configs) |

Decoder token: low 2 bits literal count+1 (0 → next byte+3); high nibble match length−2 (15 → +next byte+15); match offset low byte + token bits2..3 (3 → extended); byte-wise overlapping copy; record size bit0 selects SB-relative destination.
(audio-dispatch-initializer-closure-2026-10-08/REPORT.md; pre-consolidation:g2/analysis/audio-platform-callbacks-closure-2026-10-08/REPORT.md; audio-logger-provider-composition-2026-10-09/REPORT.md; audio-dsp-frontier-20261010/REPORT.md; audio-diagnostic-deinit-closure-2026-10-08/REPORT.md)

### 9.2 Common low-power initializer `0x47FAE8..0x47FE12`

Order: clear BOR on POA; trace disable if count 0; CPDLP (`0x47FFC4`, writes `0xE001E300`) + WIC; optional OTP; revision/INFO1 (`0x47F954`); register callbacks (`0x480434`); disable crypto/OTP; MCU memory (`0x47F204`) and SRAM (`0x47F46A`) config; clock-gate/AUDADC delay; **trim capture** block `0x47FC14..0x47FDB4`; retention (`0x4002037C` b30, `0x40020380` b16, b12); TON init/update under PRIMASK; LP init; clock-mux reset `0x44B158`; major≥0x22 → `0x400211C8 |= 6` (MRAM auto-wake). Call chain: `0x5CDD2C` → platform wrapper `0x4C2AE8` (**discards status**; then unconditional buck-active power call) → `0x47FAE8`.
- Trim capture: skipped if `0x20074F63`≠0; caches VDDC/VDDF (`0x40020044/4C`), mem (`0x40020088`), core/temp (`0x40020080`) into `0x2007426C..0x20074290` and six TON fields `0x20074294..0x200742A8`; buck active (bits4..5 of `0x40021108`==3) adds +7/+6 core by revision **without saturation** (1023 → 1030).
- INFO1 cache `0x20071948` (128 B), signature `0x1F01600D` set only on full success; failure does not roll back; initializer discards status. MCU config 5 B `{ROM mode, active DTCM, retained DTCM, active NVM, retain NVM}`; SRAM config 5 B `{active, w/MCU, w/GPU, w/display, retain}`; both discard power-dispatcher errors (SDK does not).
- `am_hal_sysctrl_clkmuxrst_low_power_init 0x44B158`: active recovery only if reset reg `0x4000885C` bit1 clear and retained `0x40008858` high16 == `0x5AF0`; **always** writes retained=0 then reinstalls signature (requests consumed even if ineligible). Request update `0x44B0D6` (cache `0x200740EC`, 6 slots CG_AUDADC/LL_AUDADC/LL_PDM/LL_I2S0/LL_I2S1/LL_USB, **no index<6 check**), ref update `0x44B0B6` (bit6). Active path powers PDM0/I2S0/I2S1/AUDADC/USB/USBPHY, overwrites R5 low nibble for GPIO15 (stock omits SDK board query, SIP GPIO136 and 1000-µs delay).
(pre-consolidation:g2/analysis/audio-clock-reset-active-2026-10-08/REPORT.md; pre-consolidation:g2/analysis/audio-clock-reset-gates-2026-10-08/REPORT.md; pre-consolidation:g2/analysis/audio-common-startup-closure-2026-10-08/REPORT.md; pre-consolidation:g2/analysis/audio-trim-initialization-closure-2026-10-08/REPORT.md; audio-info-memory-providers-2026-10-08/REPORT.md; pre-consolidation:g2/analysis/audio-gpio-providers-2026-10-08/REPORT.md)

### 9.3 GPIO, INFO, peripheral power

- GPIO getter `0x480EEE` (pin<224 checked before NULL: 5 vs 6) / setter `0x480F0C` (drive bits[11:10]≥2 needs drive-capable pad; extended pads pull bits[15:13] ∈{0,1,6}; else 7; writes all 32 bits under PADKEY `0x40010400=0x73`; pad words at `0x40010000+4*pin`).
- INFO reader `0x4D3DDA` (354 B) = SDK `am_hal_info.c` `infoX_read`: 6 spaces, SHADOWVALID bits 4/3, OTP power bit27, limits 64/512/704/1536 words, status 6/5/9, INFO1 MRAM translation after word 511, copy via `0x48086A`. Selector `0x4D3F3C` accepts spaces 1/3/5. Revision getter `0x47EF38`: cache `0x200001E8` (INFO1 word 244), refresh only on `0xFFFFFFFF` (startup value — **uncached sentinel, not a revision**).
- Peripheral power: descriptor `0x47EF18`, table `0x6BECB0` (16-B rows); enabled query `0x47F90C`; enable `0x47F5B8` / disable `0x47F7AE` (predicate `0x47F6F2`). UART domains 11–14: enable `0x40021004` masks `0x200/0x400/0x800/0x1000`, **shared** status `0x40021008` mask `0x1E00` (enable waits for whole group; disable of last member waits for "≠0x1E00"; non-last skips poll). Audio domain 30: `0x4002100C`/`0x40021010` mask 0x4, SPOT stimulus 4 (ordinary 3). OTP idx 29: `0x40021004`/`0x40021008` mask `0x08000000`.
- Stock vs SDK `am_hal_pwrctrl`: CRYPTO index **0x17** and OTP **0x1D** (different enum), peripheral narrowed to u8, **SPOT callback failure ignored** (SDK returns), OTP disable returns 3 if rev<0x22 and CRYPTO status bit21 set. Pre/post/group callbacks at `0x2007327C`/`0x20073280`/`0x20073274`; their returns are ignored.
- Trace disable `0x4D403E` (refcount byte `0x20074F5E`, clears DEMCR bit24); trace counter `0x539304` uses `0x20074F7E`.
(audio-gpio-providers-2026-10-08/REPORT.md; audio-source-candidate-20261010/REPORT.md; pre-consolidation:g2/analysis/audio-uart-power-provider-lead-2026-10-09/REPORT.md; pre-consolidation:g2/analysis/audio-uart-power-composition-2026-10-09/REPORT.md; audio-uart-group-power-2026-10-09/REPORT.md)

---

## 10. SPOT-manager power families ("PCM", `am_hal_spotmgr_pcm*`)

### 10.1 Registration and callback table

Registrar `0x480434` (668 B) zeros 60-B table `0x20073270`, reads CHIPREV `0x4002000C` and trim version `0x200001E8`, writes predicate bytes `0x20074F64..69`, installs family callbacks, invokes slot 0 initializer. Group/pre/post selection:

| Major / trim ver | Group (`+0x04`) | Pre | Post | Family |
|---|---|---|---|---|
| 0x21 / 0 | 0 | 0 | 0 | — |
| 0x21 / 1 | `0x59FD37` | 0 | 0 | PCM0.7 |
| 0x21/2,3; 0x22/0,1; 0x23/0 | `0x5A0787` | `0x5A07E7` | `0x5A07F1` | PCM2.0 |
| 0x22/2; 0x23/1 | `0x5A1739` | 0 | 0 | PCM2.1 |
| 0x22/3 | 0 | 0 | 0 | — |
| 0x23/2,3; 0x24/0..3 | `0x5A490D` | 0 | 0 | PCM2.2 |

Slot wrappers (each reads slot twice, NULL → 0): before-override `0x480358`/`+0x14`, before-enable `0x48036E`/`+0x18`, after-enable `0x480384`/`+0x1C`, TON-init `0x4803AC`/`+0x20`, TON `0x4803C2`/`+0x24` (args u8), tempco-suspend `0x4803DC`/`+0x28` (slot 10; **no stock family installs it**, SDK does under `NO_TEMPSENSE_IN_DEEPSLEEP`), timer service `0x48039A`/slot 11 `+0x2C`, LP-auto init/enable/disable `0x4803F2/0x480408/0x48041E` (`+0x30/+0x34/+0x38`), generic control `0x480312` (`+0x04`), pre/post `0x48032C/0x480342` (`+0x0C/+0x10`). Older offline symbol names for these were wrong; use addresses.
Buck override `0x47FE6C`: three RMWs at VRCTRL `0x40020060` (SIMOBUCKOVER b16, CORELDOOVER b0, MEMLDOOVER b5).
(audio-uart-power-composition-2026-10-09/REPORT.md; audio-platform-callbacks-closure-2026-10-08/REPORT.md; pre-consolidation:g2/analysis/audio-pcm-registry-interface-successor-2026-10-09/REPORT.md; pre-consolidation:g2/analysis/audio-early-pcm-dispatch-closure-2026-10-09/REPORT.md; audio-uart-group-power-2026-10-09/REPORT.md)

### 10.2 Shared request ABI

Internal 19-B request: u32 masks `dev+0, audio+4, memory+8, SSRAM+12`, bytes `temp range+16, CPU state+17, GPU+18`. Actions: 0 CPU byte, 1 GPU byte, 2 float °C → lower/upper bounds at +4/+8, 3 device OR (if enable), 4 audio OR, 5 memory assign, 6 SSRAM assign (if enable); ≥7 or missing metadata → 6. UART enable passes the **shared group mask `0x1E00`** as device request. Internal power actions, not wire opcodes. Temperature wrapper `0x480028` (S0 float) → `0x480312(action 2)`, zeros bounds on failure.
(audio-platform-callbacks-closure-2026-10-08/REPORT.md; pre-consolidation:g2/analysis/audio-pcm21-control-closure-2026-10-08/REPORT.md; pre-consolidation:g2/analysis/audio-uart-newer-callback-composition-2026-10-09/REPORT.md)

### 10.3 PCM2.2 (newest silicon)

- Update `0x5A490C`: gate SIMObuck `0x40021108` bits4..5 → signature `0x1F01600D` at `0x2005665C` → plan/apply. Classifier `0x5A1E8C`: `[-273,-20),[-20,0),[0,50),[50,1000)` with 2 °C hysteresis bounds `[-273,-20],[-22,0],[-2,50],[48,1000]`. Planner `0x5A45D0`, state `0x5A421C`, prepare `0x5A410C` (timer query `0x48D620`), selector `0x5A4334`, step `0x5A44BA`, apply `0x5A453C`, TON `0x5A423C`, calibration init `0x5A4D48`, reset `0x5A4E0C`. Corrected flag rule: `0x20074F6A = (profile−9u)<3 && byte 0x20004540 != 7`.
- UART planner outputs (active buck, valid sig): temp 0/1/2/3 with CPU0 → profiles 7/6/5/4 TON6; CPU1 → 15/14/13/12 TON7; temp 255 → error 5 (UART wrapper still returns 0).
- 27-entry transition table at `0x200002A8` (startup data):

| Idx | Entry | Behaviour | | Idx | Entry | Behaviour |
|---|---|---|---|---|---|---|
| 0 | `0x5A1F04` | VDDF boost 50µs, selector 20µs; cancels matching active timer (TON, VDDC, stop, pending 26) | | 14 | `0x5A34CA` | restore VDDF, no TON |
| 1 | `0x5A20E8` | VDDF/VDDC boost 50µs, core 5µs, CPU/AOR switch 20µs | | 15 | `0x5A35A4` | LV trim, core, VDDC |
| 2 | `0x5A22C0` | 2-phase: VDDC boost, 50µs timer, pending 2 | | 16 | `0x5A36AC` | LV trim only |
| 3 | `0x5A2462` | TON, VDDF double boost | | 17 | `0x5A3798` | LV boost/core/restore, no delay |
| 4 | `0x5A2586` | load trims, TON, clear AOR/CPU bits | | 18 | `0x5A38CE` | `2*p0_VDDF−new` boost, no TON |
| 5 | `0x5A26BE` | TON, LP/domain/HP attempt | | 19 | `0x5A3AB0` | LV boost 50µs |
| 6 | `0x5A28C0` | restore VDDF, TON | | 20 | `0x5A3BCC` | core + 5µs |
| 7 | `0x5A29A0` | TON, 0.9× VDDF margin, timer 50µs, pending 7 | | 21 | `0x5A3CC6` | phase 1 + continuation flag `0x20074F77` |
| 8/10/23 | `0x5A2C30/0x5A2E10/0x5A3FE8` | publish + TON | | 22 | `0x5A3E80` | VDDC boost, core, VDDF restore, TON |
| 9 | `0x5A2D24` | restore VDDF, TON | | 24–26 | `0x5A40B0/B2/B4` | no-op |
| 11 | `0x5A2EEA` | LP/HP attempt + VDDF boost | | 12 | `0x5A3122` | VDDF boost/core/restore, no TON |
| 13 | `0x5A326C` | TON, 0.9 margin, LP/HP | | | | |

- Completions: dispatcher `0x5A40CA` (IRQ82 → vector word 98 at `0x438188` = `0x4D58A7` → `0x48039A` → slot 11) runs 2b `0x5A23F8` or 7b `0x5A2B14` per pending byte `0x20004540` then sets 26; timer stop `0x4802CE` (releases clock client (4,49), NVIC82). 21b `0x5A3E24` via post wrapper `0x5A40B6` uses **current** profile `0x200002A0`. Timer: init `0x4801FC` (CTRL0 `0x110`), start `0x480240` (duration ×6), restart `0x48028A`; timer active `0x400083E0`, compare status `0x40008064`.
- Data: calibration word `0x20056660+4*profile` = VDDF[6:0], coreLDO[16:7], tempco[20:17], VDDC[27:21]; `0x200566C0` LV trims; pending `0x200742D4..E8`; current/last profile `0x200002A0/A4`.
- **Stock vs SDK 5.1.0 differences:** stock 7/13 use `uint32 (new−p1)*0.9f` (float `0x3F666666`; wraps → clamp 127); completions 2b/7b and core settles 5 µs vs SDK 10 µs; 12/14/15/18 omit TON; 17 omits 50 µs; 11 adds VDDF boost; 0/1/21 ignore cache enable/disable errors (cache guard `0xE001E300` bits8..9); stock lacks stimuli 7/8 and differs in temperature/trim init. Sequence 0 reads timer-active conditionally twice (a cached snapshot is wrong).
(pre-consolidation:g2/analysis/audio-transition-producers-closure-2026-10-08/REPORT.md; pre-consolidation:g2/analysis/audio-transition-timer-closure-2026-10-08/REPORT.md; audio-transition-snapshot-successor-2026-10-09/REPORT.md; audio-platform-callbacks-closure-2026-10-08/REPORT.md; pre-consolidation:g2/analysis/audio-uart-newer-planner-composition-2026-10-09/REPORT.md; pre-consolidation:g2/analysis/audio-uart-transition-provider-composition-2026-10-09/REPORT.md)

### 10.4 PCM2.1

- Control `0x5A1738..0x5A1BB6`: returns success **without** recording temperature when buck inactive (SDK records it); bad signature → 1; CPU 2..4→0/1 updates byte `0x20074F76` only; HP→LP defers state change until a changed plan is applied; invalid temperature → range 4, return 6. Classifier `0x5A0A70`.
- Children: prepare `0x5A0C20` (forced-buck byte `0x20074F7B`; range3, low-30 device bits, audio mask `0x4C4`, SYSPLL bit29, STIMER/timer clocks), state-change `0x5A0D44`, planner `0x5A13E8` (memory/SSRAM masks ignored; unknown temperature → 5, SDK → profile 20; profile mask `0xF00FFF`, TON mask `0xFF00F`; profiles 0..15, special 16..19), apply `0x5A0FC4` (calibration `0x20056660+4*p`; direction from voltage-order tables `0x200001F4`/`0x20000244`; delays 50/200/2000 µs; I-cache toggled crossing into 8..15).
- Completion: TON `0x5A0D9C` (core+14, mem+6 temporarily; selector 7 reads VDDF `0x40020354` but writes `0x40020358`), timer publish `0x5A0AE8` (core+7 cap 1023, increment at `0x200742C8`), boost removal `0x5A0B54`, buck completion `0x5A0B9C`, timer ISR `0x5A0BCC` (installed slot 11 as `0x5A0BCD`), before-override `0x5A1BBC`, before-enable `0x5A1BCC`, after-enable `0x5A1BEC`, calibration init `0x5A1C18` (16 INFO1 profile words; profiles 16..19 from 4..7 with low-7 VDDC from 12..15; no profile 20; VDDF comp fixed 31), reset `0x5A1DA4` (needs `0x40021008/10`==0, enables OTP 29, requests −40 °C, waits `0x400083E0` bit0 2500 µs; 1/4/0).
(audio-pcm21-control-closure-2026-10-08/REPORT.md; pre-consolidation:g2/analysis/audio-pcm21-children-closure-2026-10-08/REPORT.md; pre-consolidation:g2/analysis/audio-pcm21-completion-closure-2026-10-08/REPORT.md; pre-consolidation:g2/analysis/audio-pcm21-reset-closure-2026-10-08/REPORT.md)

### 10.5 PCM0.7 / PCM2.0 (earlier silicon)

- Variant initializer `0x5A08E4`: flags `0x20074F6E` (0x21 r2), `0x20074F6F` (0x21 r2/3, 0x22 r0), `0x20074F70` (0x22 r1, unscreened 0x23 r0); screening date from FT1REV (y24/m12/d≥20 or y≥25). No-op callbacks `0x5A0018`, `0x5A0A6C`.
- GPU on/off: PCM0.7 `0x59FBAC`/`0x59FCA2` (switch helper `0x59FB70`); PCM2.0 `0x5A0328`/`0x5A05E0` (core +12 cap 1023, VDDF +15 if flag `0x20074F6F`, four rail-short controls). Repeated GPU-on is **not idempotent** (two on + one off leaves VDDC+9/VDDF+15).
- Temperature `0x5A00FC`: `[-273,35),[35,50),[50,1000)`, bounds `[-273,35],[33,50],[48,1000]`; publication `0x5A00C8` (range `0x20074F74`, pending `0x20074F72` when postponed `0x20074F71`) or apply `0x5A001C` (VDDF only: base `0x20074270`, −10 for range 0/1, +15 if GPU on (`0x40021004` b18) and flag 6F; cap 127). Postpone `0x5A07E6`, pending `0x5A07F0` (applies **latest** range only; clears pending even if gate blocked the write — no replay).
- Sleep prep `0x5A0204` (gate `0x20074F67`), TON init `0x59FDC2` (defaults VDDC 14/31, VDDF 21/31, LV 11/11; cache `0x2000453A..F`), TON update `0x59FE5A` (data `0x789FE0` rows GPU OFF/LP/HP × CPU LP/HP), LP-auto init `0x5A085E` (FCNT 1000, thresholds 800/450/600/250), enable `0x5A08B6` (flag `0x20074F73`), disable `0x5A08CA` (no-op if flag clear). Before/after-enable: earlier `0x59FD82`/`0x59FDA8` (core −6; mem trim 0/ctrl 1), middle `0x5A081C`/`0x5A0842` (core −7; trim 1/ctrl 2).
(pre-consolidation:g2/analysis/audio-early-pcm-gpu-closure-2026-10-08/REPORT.md; pre-consolidation:g2/analysis/audio-early-pcm-pending-closure-2026-10-08/REPORT.md; audio-trim-initialization-closure-2026-10-08/REPORT.md)

---

## 11. Upstream source and toolchain identification

| Component | Finding | Source |
|---|---|---|
| Ambiq HAL | Apollo510 HAL first appears in SDK 5.1.0 (pin `5efc0228`); stock bodies match selected `am_hal_uart`, `am_hal_itm`/TPIU/debug, `am_hal_info` (`infoX_read`), `am_hal_utils` (delay/status wait), `am_hal_clkmgr`, `am_hal_sysctrl` clkmuxrst, `am_hal_spotmgr_pcm2_1/2_2`, `am_hal_pwrctrl` — each with documented **stock-specific deviations** (§5.5, §8.3, §9, §10); wholesale substitution changes behaviour | audio-logger-stock-provider-closure-2026-10-09/REPORT.md; audio-uart-tx-ownership-2026-10-09/REPORT.md; audio-platform-callbacks-closure-2026-10-08/REPORT.md; audio-source-candidate-20261010/REPORT.md |
| `am_util_stdio` | text formatter = SDK 3.2.0 `release_sdk_3_2_0-dd5f40c14b` | audio-main-formatter-source-successor-2026-10-09/REPORT.md |
| FreeRTOS | queue/list/tasks/stream-buffer/event-group bodies = V10.5.1 `def7d2df`; `osThreadFlagsSet` = CMSIS-FreeRTOS `d213f261` | audio-thread-flags-closure-2026-10-08/REPORT.md; audio-uart-rx-stream-ownership-2026-10-09/REPORT.md; audio-queue-cmsis-source-closure-2026-10-09/REPORT.md |
| Exact-byte stock bodies | PRIMASK save `0x473940` (8 B), BASEPRI save/restore `0x5FA0A4`/`0x5FA0BA` (22/14 B), three 10-B fatal asserts reproduce byte-exact from C/inline asm | audio-source-candidate-20261010/REPORT.md |
| Math | `floorf/roundf/ceilf/fmodf` and `asin` not attributable to newlib/picolibc/SDK; asin consistent with IAR DLIB | audio-float-runtime-closure-2026-10-08/REPORT.md; audio-dsp-frontier-20261010/REPORT.md |
| ABI | compact enums required (`-fshort-enums`: public PCM2.2 selector footprint mismatches with wide enums); stock hard-float S0 for temperature/math leaves | audio-platform-callbacks-closure-2026-10-08/REPORT.md; audio-source-candidate-20261010/REPORT.md |

Emulation caveats (Unicorn 2.1.4): continuous execution mishandles Thumb IT state after stock memcpy/memset (`0x43C10E–0x43C116`) — step one instruction at a time; M33/M7 profiles reject `VCVT.F32.F64`; `csel`/`cset`/`VSELGT` unsupported; first-VFP-use resets FPSCR; broad memory hooks altered execution (skipped `LDR`). (audio-queue-cmsis-source-closure-2026-10-09/REPORT.md; audio-main-formatter-source-successor-2026-10-09/REPORT.md; audio-notification-pcm-2026-10-06/REPORT.md; audio-source-candidate-20261010/REPORT.md)

---

## 12. Stock bugs and quirks (index)

1. BUXX CRC-flagged empty body skips CRC; reader writes header before capacity check (§5.2).
2. Codec close/init state mismatch after failed close; failed enable not rolled back; host init ignores baud error (§5.4).
3. UART3 RX ring evicts oldest bytes; logger RX callback drops rejected suffix (§5.4, §6.2).
4. One-byte codec reader sign-extends timeout and fails to reach deadlines across tick wrap (§5.3).
5. Timer aux freed before daemon processes the delete; due callback can read freed aux (§7.6).
6. Audio exit acks before cleanup; queue delete has no drain (§1.4, §7.4).
7. Clock manager: HFRC2 error overwrite, SYSPLL late-lock ownership retention, HFRC leaves HFADJ on, CLKOUT drive check after acquire (§8.2, §8.3).
8. Clock-mux reset always consumes retained requests; request update lacks index check; trim capture adds without saturation (§9.2).
9. PCM registry overwrites rows; unregister lacks mode bound (§2.4).
10. I2S/codec HAL helpers dereference handle before NULL check (§2.5, §5.5).
11. GPU-on not idempotent; pending temperature work cleared without apply (§10.5).
12. SPOT callback failures ignored by power enable/disable and UART power wrapper (§9.3, §10.2).
13. Status-wait helpers compare against unmasked expected value (§8.4).

## 13. Open blockers / unknowns (as last stated)

- No live trace of vector/NVIC/PendSV delivery, task population or daemon/callback interleaving: concurrency and lifetime hazards above are instruction-ordering facts only.
- Authentic INFO1/OTP calibration and chip revision unknown → running SPOT family (PCM0.7/2.0/2.1/2.2) and trims undetermined (startup trim word is `0xFFFFFFFF`).
- Unresolved/unowned bodies: extended logger `0x43D574`, short formatter production domain (531 unresolved format pointers), `asin 0x43C260` (needs licensed IAR DLIB source), `osDelay`/`vTaskDelay` composition, timer drain `0x47E97A` full matrix, `osEventFlagsSet` with waiters, `codec_irq_service` full RX/memset path, file-heap TLSF pool/failure path, transaction send `0x57C512`, callback registrar `0x480434` matrix, power enable/disable (13 active families), UART thread `0x5417D6`, DSP enable/disable full DMIC/I2S chain.
- Logger: no static writer found for flag `0x20074F4E`; the live sink actually installed at boot is not traced.
- Physical meaning of GX8002 control responses, real baud/clock/power readiness and elapsed times are unmeasured.
(pre-consolidation:g2/analysis/audio-provider-recheck-2026-10-09/REPORT.md; pre-consolidation:g2/analysis/audio-ledger-current-rescan-20261009T212351Z/REPORT.md; audio-source-candidate-20261010/REPORT.md; audio-dsp-frontier-20261010/REPORT.md)
