# XIP lifecycle, mode dispatch and application boundary

Status: partial P2 evidence ready for independent review. This pass covers six lifecycle roots, thirteen directly source-correlated mode/registration/queue bodies and five application callbacks: **24 non-overlapping bodies, 1,446 instruction bytes**. All raw decompiles completed. `result.json` verifies every Ghidra instruction address is also present in independently generated GNU objdump output; this validates decoder coverage at these bounded bodies, not complete behavior or silicon execution.

The locked bundle and codec hashes are rechecked before each run. Canonical XIP bytes equal codec [50576,87060), with reviewed conditional base **0x10203004**; the SRAM TWS tick uses reviewed conditional base **0x10023400**. Each body has image/child/codec/runtime spans and byte hashes in `bodies*.json`. `mapping.json` preserves the full XIP route and its external aperture/selection/PMU premises. Installed tooling, prior evidence, canonical ledgers and gates are unchanged.

## Six lifecycle roots

| Entry | Body bytes | Instruction/source correlation |
| --- | --- | --- |
| 0x102078a4 | 354 | `LvpSystemInit`: cache and DMA initialization; console port 1/115200; wake-source query; cold/WDT-only logging, flash metadata, frequency/LDO queries, KWS/board/GPIO/RTC setup; unconditional timer, IRQ, device-list, SPI-master and PMU initialization. Public `lvp_system_init.c` provides this ordered skeleton. |
| 0x102085a4 | 68 | `LvpInitMode`: loop=1 and index=0 at 0x2002e6e4/0x2002e6e8; compares requested type against two static records; selects IDLE if unmatched; calls selected buffer-init, then selected init(0xffff), ignoring both return statuses; returns selected record type. |
| 0x10208cd4 | 82 | `LvpInitializeAppEvent`: initializes queue (0x2002ecd8, buffer 0x2002e880, size 64, member 8), calls non-null AppInit, registers suspend/resume callback+private pairs, initializes watchdog (3000,2999,0x10208c98,NULL), returns 0. |
| 0x102085f8 | 26 | `LvpModeTick`: loads current index, conditionally calls selected non-null tick callback, then returns loop word. No index bounds check is present. |
| 0x10208d48 | 70 | `LvpAppEventTick`: zeroes two-word APP_EVENT; gets one misc-queue event, calls AppEventResponse when queue nonempty and pointer/callback non-null; calls AppTaskLoop when non-null; calls source-correlated UART async tick and watchdog ping helpers; returns 0. |
| 0x10207a7c | 2 | `LvpSystemDone`: `jmp lr` only, agreeing with empty public shutdown function. |

`system-init-literals.json` binds startup literal-pool words and source strings. The shipped board label is `grus_gx8002b_dev_1v`, build string `2026-03-26, 17:07:25`, release constant `0x42555858`, and CPU log says fixed frequency. These are compiler/build clues, not a measured board identity. Flash vendor tests and print strings match the public PUYA/ESMT/ZBIT branches. The printed MCU-version pointer names an empty string. Fixed call/log sequences corroborate selected preprocessing branches; they do not establish an exhaustive original autoconf file.

## Static mode dispatch resolved

`mode-table.json` reads exact immutable XIP words at 0x1020b1bc: two pointers to records 0x1020b1c4 and 0x1020b204. Their five-word layouts match public `LVP_MODE_INFO` in `lvp_mode.h`.

| Mode | Type | Init | Done | Tick | Buffer-init |
| --- | --- | --- | --- | --- | --- |
| IDLE | 0 | 0x10208634 | 0x10208624 | 0x1020861c | 0x10208620 |
| TWS | 1 | 0x10208670 | 0x1020864c | 0x10026358 | 0x10208644 |

All eight targets were exported and checked against native instructions. IDLE tick is a two-byte return; buffer-init returns 0; init/done print their public IDLE log strings, with init returning 0. TWS buffer-init calls 0x10206dc0 and returns its result. TWS done clears 20 bytes at 0x2002e6ec, calls KWS teardown and audio teardown candidates, prints the TWS exit string and returns. These source relationships are candidates pending helper review.

TWS init initializes a 56-byte queue of eight-byte MODULE_INFO members, calls KWS initialization candidate 0x10208944, queries the already archive-matched wake-source function, and calls KWS callback registration candidate 0x10206d90. If previous mode equals 0xffff and wake source is above 1, it calls resume-audio candidate 0x10207660; otherwise it calls audio-init candidate 0x102073bc and returns -1 after logging on nonzero result. Its success path writes state word 2 and counter 50 at offsets 0x4c/0x50 from its state base, then returns 0.

The 90-byte SRAM TWS tick gets one MODULE_INFO from the queue. For module_id=0x100 it calls decoder candidate 0x102088f8 and a helper with argument 1. If the context byte at +0xd is nonzero, it constructs an APP_EVENT from that byte and the context word at +8 and calls event-enqueue candidate 0x10208cc0. When the state word at +0x4c equals 4 and busy-check candidate 0x102077f8 returns 0, it calls suspend candidate 0x10207808 with argument 13. Public `lvp_mode_tws.c` corroborates these branches and structures. Audio/NPU/decoder effects remain a separate transitive frontier.

This closes the immutable table's immediate callback set. Mutable index/loop writes elsewhere, lifecycle switching and state invariants have not been exhaustively analyzed, so it does not establish every possible future indirect target.

## App registration and queue bodies

Suspend wrapper 0x10208ca0 first stops watchdog, then calls non-null AppSuspend(private), returning 0. Resume wrapper 0x10208c7c first starts watchdog, then calls non-null AppResume(private), returning 0. Watchdog callback 0x10208c98 calls reboot candidate 0x10203bac. Their public conditional source branches match the instructions.

`LvpQueueInit` at 0x10206f9c is 20 bytes: stores member size, buffer pointer, size rounded down to a member-size multiple, zero tail and zero head. `LvpQueueGet` at 0x10206fb0 is 74 bytes: returns 0 for head=tail; otherwise copies member_size bytes one by one from buffer[(head+i)%size], updates head=(head+member_size)%size, returns 1. Source `lvp_queue.c` and header field order match all these effects. The reachable queue initialization here uses positive 64/8 and 56/8, so its division is defined under the observed arguments; arbitrary zero-divisor behavior remains an ISA obligation for whole-function semantics.

The initialized application data introduces a useful source clue and a distinct boundary. `app-table.json` binds canonical SRAM child [0x3938,0x395c): initial app_core_ops word 0x20026d3c at declared DRAM 0x20026d38, followed by a 32-byte LVP_APP record. Public `link.ld` explicitly reserves a DRAM text-size placeholder then emits `.stage2_sram_data` into DRAM; that corroborates the initializer coordinate relation. Actual IRAM/DRAM visibility and subsequent mutation remain external/unreviewed.

| App field | Initial target/value |
| --- | --- |
| app_name | 0x1020b649, `sample app` |
| AppInit | 0x10208e4c |
| AppEventResponse | 0x10208f04 |
| AppTaskLoop | 0x102091bc |
| AppSuspend | 0x10208dec |
| suspend_priv | 0x1020b654, `SampleAppSuspend` |
| AppResume | 0x10208dcc |
| resume_priv | 0x1020b665, `SampleAppResume` |

All five initialized application targets were additionally exported (450 instruction bytes). They differ materially from the public sample app stubs despite sharing names and strings. AppInit is an idempotent state-guarded setup, AppEventResponse handles events 100/101/91 with context/state and buffered-data helpers, and AppTaskLoop processes pending state changes and a countdown. In particular AppTaskLoop is 128 bytes rather than public `return 0`, and AppEventResponse has a Ghidra `Type propagation algorithm not settling` warning. Native instructions still decode at all body addresses; raw C is not adequate reviewed pseudocode for this application layer.

## Stop boundary and exact next work

The public lifecycle structure, immutable mode records, initial app registration layout, queue behavior and callback scaffolding have been pushed through the bounded source-correlated chain in this pass. The newly exposed firmware-specific app helper family at 0x102096fc, 0x1020975c, 0x10209770, 0x1020979c, 0x102097c8, 0x10208ff0, 0x1020913c and 0x10208e80 requires a new coherent application-state/protocol task; public sample C does not define its behavior. Callback state can also change outside this scope, so full dynamic dispatch closure remains unresolved.

Audio, decoder/NPU and PMU providers reached by TWS init/tick form another coherent subsystem task. Matching public driver archives give useful symbols/relocation evidence, but their absent C and hardware effects are not eliminated by the lifecycle skeleton. Further work can recover shipped body semantics; no byte-identical source build, runtime success or global source-exhaustion claim is made here.

The next exact actions are independent review of these 24 body/mapping records, a bounded firmware-specific app-state/protocol analysis, and a separate TWS audio/decoder/PMU task. Prior evidence remains intact; no new source downloads were necessary in this worker scope.
