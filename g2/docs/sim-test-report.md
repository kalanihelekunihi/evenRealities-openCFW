# G2 simulator test report (2026-10-26)

## Simulator
- Repo: ~/Repo/g2-firmware-emulator (origin PaulMcMillan/g2-firmware-emulator, master, HEAD f30527c, 2026-09-24).
- `git fetch` showed the tree clean and 0/0 ahead/behind, so it was already current and no merge was needed.
- Model: Renode Apollo510 + Unicorn, pinned to 2.2.9.22 images.
- Setup (all in gitignored dirs): .venv with `pip install -e '.[test]'` and pyelftools; bootstrap-firmware (g2flash clone, artifacts/mainapp.bin); bootstrap-renode (Renode 1.17.0 built from source; needed `brew install cmake`).

## Host test suite
- Command: `pytest -k "not native" --continue-on-collection-errors`.
- The run stopped at about 47% (the session was interrupted); about     2969 F and     2499 E so far. Log: /tmp/sim-host-pytest.log.
- Upstream says plain pytest is not a passing suite.
- 16 collection errors come from `ValueError: Changed original marker producer` (src/g2emu/renode_log_marker.py:101), in test_imu_edmp_*, test_renode_local_abort*, and test_renode_log_marker. This is an upstream sim bug, not ours.

## Firmware runs (Renode display.resc, harness generated/opencfw/runsim.sh)
| Image | Result |
|---|---|
| stock 2.2.6.10 | RTOS running after 3 s (PC 0x44adfa) |
| patched 2.2.9.22 | RTOS running after 3 s (PC 0x44d706) |
| ours w22 final | **Hung in main**: `b .` after kernel_start (blx to stock address 0x4c9b49) |
| ours sim1..sim5 | Each fix below exposed the next fault (assert, then INVSTATE HardFaults) |
| ours sim6 | Scheduler and threads start and there is no HardFault. Reads of 0xA5A5A5A4/8 (FreeRTOS stack-fill pattern used as a pointer) in AttRegister (0x508206) and xEventGroupSetBits (0x5cc8ac): a handle cell is never initialized. **Next item to chase.** |

| ours sim7b (global RAM rewrite) | HCI vendor cmds sent, then ROM nv_program to 0x2014B3A0 status=2, hang in hciCmdSend self-branch, WDT reset at ~20 s |
| ours sim8 | nv_program 0x007FE000 status=0; HCI_Reset sent and its Command Complete read, but never parsed (reset retried every ~10 s) |
| ours sim11 (current) | 21 HCI commands, identical to stock through LE_Read_Local_P256 (0x2025) except the BD address (zeros vs 69DF226531FC); stalls there and sends HCI_Read_Buffer_Size (0x1005) on the 10 s HCI timer |

### Milestones, ours vs stock (Renode display.resc, 20 s)
| Milestone | stock 2.2.6.10 | ours sim11 |
|---|---|---|
| Reset → main, .data/.bss init | yes | yes |
| FreeRTOS scheduler + threads | yes | yes (no HardFault, no assert) |
| OTA flag nv_program (0x007FE000) | status=0 | status=0 (fixed in sim8) |
| em9305 boot vendor cmds (FD01 ×2) | yes | yes |
| HCI_Reset + Cordio reset sequence | 21 cmds through 0x2025 | same 21 cmds (BD addr zero) |
| LE_Encrypt ×32 / Set Random Addr / Adv params+data+enable (BLE up) | yes | **no**: stalls after 0x2025 |
| Display panel frames latched (mspi0.panel) | 2 frames | **no** |
| Watchdog reset | none | none in sim11 (sim7b had one) |

The fixed ELF is in g2/build/g2c-sim11-final-apollo-main/ (0 undefined). The w22-final ELFs are untouched.

## Fixes applied (each file has a "Sim-test fix" evidence comment; backups in .waves/sim-bak/*.orig)
1. hal/uart/uart-thread/display_uart_thread_manager_state.c: stock pointer bytes 0x4c9b49/0x4c9b71 replaced with thread_manager_kernel_start_4c9b48/thread_manager_deinit_4c9b70. This fixed the boot hang.
2. ble/ble-msgrx/display_ble_msgrx_manager_state.c: threadBleMsgRxInit/Deinit (stock 0x48ee68/0x48ee94).
3. app/device-manager/display_device_manager_state_prefix.c: device_mgr_fn_004c6240/_004c64a4.
4. storage/file/file-heap-free.c: literal 0x200748f8/0x20074abc replaced with g2_codec_heap_mutex/g2_codec_heap_pool, matching allocate and realloc. This fixed the lfs_deinit→free assert at line 1086.
5. rtos/thread/thread.c + rtos/thread-runtime/thread_runtime_cells.c: the uart init callback is now +0 of audio_display_driver_manager (stock 0x20000658 = Disp_ThreadInit). Before, it was a separate zero cell, so the code did `blx 0`.
6. drivers/peripherals/ring-thread/display_ring_thread_manager_state.c: thread_ring_create/terminate (stock 0x4c4da4/0x4c4dd0). Fixed an INVSTATE fault.
7. ble/ble-msgtx/display_ble_msgtx_manager_state.c: threadBleMsgTxInit/Deinit (0x475348/0x475374).
8. audio/master-dispatch/comm_wsf_state.c: audio_ble_wsf_thread_state is now initialized {threadBleWsfInit, threadBleWsfDeinit}, per stock .data init at +0x4068. It was zero.
9. drivers/display/display-uled/display_driver_uled_option_* (4 files) + drivers/power/npmx-watchdog/kick.c: literal 0x20070f78 replaced with &g2_npmx_instance. Fixed a HardFault in the npmx watchdog kick.

10. Global stock-RAM rewrite (issue 1), tools in .waves/sim-fix/ (rammap.py, ctx.py, plan.py, apply.py, reloc.py; per-file backups in .waves/sim-fix/bak/):
    - 747 literal uses in 121 files now go through a named object: 240 rewritten symbol-relative to an existing C object, 507 to 52 new objects in system/stock-ram/stock_ram_cells.c (new sources.json unit). Form: `((uint32_t)(uintptr_t)g2ref_SYM+0xOFFu)` with `extern unsigned char g2ref_SYM[] __asm__("SYM");`.
    - GUESS: each new object's size is the gap to the next known stock cell, capped at 64 KiB; the stock extent is not recovered.
    - 12 objects that fall in the stock .data init ranges carry the stock init bytes (.waves/init_2000*.bin). In those, 53 words pointing into stock RAM were relocated to the owning object and 52 stock Thumb code pointers to our functions (g2/symbols/apollo_main.tsv names). Left as stock values, flagged: 23 RAM words with no owning object, 21 code pointers 0x5a1f05..0x5a3fe9 (unnamed table at stock 0x200002a8) + file_heap_reallocate, and 1,937 non-code flash words (rodata pointers; not checked).
    - Not rewritten: 264 literals with no cast/macro context (nanopb field words, bit masks, {reg,addr} tables; need manual review), 23 excluded (0x20000000 exactly, stack 0x2007d000..0x20080000). Conflict at 0x20000064 (two objects) unresolved.
11. Stock-pinned (layout genuinely required): link/g2-apollo-main.ld places .bss.opencfw.ota.bootloader_flag at MRAM 0x007FE000 (NOLOAD), shared with the secure bootloader; evidence: stock run logs nv_program destination=0x007FE000. Without it nv_program returned status=2. An ASSERT keeps the image below it.
12. ble/ble-hci/display_ble_hci_cmd_public.c: hciCmdSend branched to audio_ble_hci_cmd_send, which sources.json aliases back to hciCmdSend, so it was `b.w .` (sim7b ELF 0x469ae0). It now branches to audio_ble_hci_cmd_send_body.
13. sources.json: removed alias display_driver_nema_mode_513924 → audio_uart_display_graphics_blend_513924 (same self-branch, 0x48da0c) and linked the real encoder graphics/ambiq-gpu/ambiq-gpu-blit/nema_mode.c.
14. Init-data relocation (fix 10) fixed the HCI RX path: stock cell 0x20000dac held the stock RX buffer pointer 0x200704ec, so events were parsed from an empty stale buffer.

### Current BLE stall (sim11, debug trace s11d)
The em9305 model answers 0x2025 with Command Status (040F0400012520) and then sends the LE Meta P-256 Public Key Complete event (043E42 08 ...). Our SecEccHciCback (0x50d2a8) is called with it. Stock goes on to send 32 LE_Encrypt (0x2017) and then advertising setup. Ours sends nothing more until the 10 s HCI timer fires. Next step: trace SecEccHciCback → the sec/DM handler message → DmDevReset complete (likely another unrewritten or none-context cell). The BD address being zero (0143FC06 000000000000) is a separate issue (production-data/KV source).

## Remaining issues, ranked
1. **Split-brain RAM cells (systemic, highest).** 1,905 literal stock SRAM addresses in 544 files. 478 of those addresses also exist as named C objects (972 uses) that our linker places elsewhere, so writers and readers disagree. Fixes 4, 5 and 9 were instances of this. Recommended global fix: pin each named object at its stock address (`file_heap_ram_cells.ld` shows the intent, but it is not included in the link), or mechanically rewrite the literals to the symbols. List: /tmp/absram.json.
2. **Uninitialized handle at runtime**: the 0xA5A5A5A5 deref in AttRegister / xEventGroupSetBits, most likely another instance of #1.
3. **Stock flash literals**: 278 `(uintptr_t)0x4..0x7xxxxx` string/table pointers, mostly on log/assert paths. They print garbage or crash when hit.
4. Data tables holding stock code pointers: 8 found and fixed. The .data scan (/tmp/datascan.py) is now clean.
5. Not yet exercised in the sim: display panel output, BLE (the sim's em9305 is a synthetic controller), and the em9305/touch/codec images.
6. Sim-side issues: the GPU ring-stop warning (also seen with stock? not yet compared), and the upstream marker-producer collection error.

## Batch sim12: BLE stall after SecEccHciCback fixed (2026-10-26)

**Root cause.** AttsCalculateDbHash asks WsfBufAlloc for 0x204 bytes. The largest WSF pool is 480 bytes (the same as stock), so the allocation returns NULL and the hash is skipped. With no hash there are no LE Encrypt commands and no advertising. Our ATT database was bigger than stock's. Evidence comes from hooking AttsAddGroup in both images (sims stk12 and our12) and dumping the attribute tables:

| group | stock (handles, attrs) | ours before |
|---|---|---|
| GAP | 1-7 | 1-7 |
| GATT | 16-23: 8 attrs, no 2B3A | 16-25: extra Server Supported Features pair |
| DIS | 48-58: 11 attrs (2A29/2A24/2A25/2A26/2A27) | 48-66: plus 2A23, 2A28, 2A2A, 2A50 |

**Fix 15.** Both changes are in `ble/svc-g2c/svc_core_g2.c` and `svc_dis_g2.c`, with evidence comments. Backups are `.waves/sim-fix/bak/*.orig`.
- GATT end handle is set to 23.
- DIS uses a stock-shaped 11-attribute list. Its characteristic declarations are byte-identical to the stock values at 0x78e95c..0x78e97c.

**Result (sim12; s12e with em9305 logging).**
- Build: 0 undefined. Datascan went from 20 to 21; the new hit is not yet reviewed.
- The HCI command sequence now matches stock all the way through: 31× LE Encrypt (0x2017), then 0x2006, 0x2008, 0x2009 and 0x200A (advertising enabled).
- One remaining difference: 4× LE Rand (0x2018) where stock has 2.
- BD address is still zeros. That is task 2, which is next.

## Batch sim13: BD address fixed; LE Rand and data-scan items explained (2026-10-26)

**BD address.** I traced where stock gets its address by putting write watchpoints on stock RAM (sims stkbd–stkbd4):
- nvdbMacDefaultInitialize (0x5d9f48) writes the MAC into the nvMAC record at 0x200038e4+1.
- _bleAdvNameSet (0x46dd44) reads it through the pointer table at 0x20003838, word +12, and passes it to HciVscSetCustom_BDAddr (0x4b4cd2).
- That copies it to g_BLEMacAddress (0x20074148), which HciVscUpdateBDAddress sends with 0xFC43.

Our `audio_ble_adv_config_state` still held the raw stock words (200038f0 20003994 200038d4 200038e4 200038f4 20003950 200038d8 0). Those addresses point into unrelated objects in our layout.

**Fix 16.** `ble/ble-adv/display_ble_adv_config_state.c` (backup: `.waves/sim-fix/bak/*.orig`) now holds relocations to our definitions of the same records. Record identities come from `include/g2_nvdb.h`:

| stock address | record | our symbol |
|---|---|---|
| 0x200038f0 | nvProdMode | g2_uart_product_mode_state |
| 0x20003994 | nvSysDt | display_driver_ratio_cells_20003994 |
| 0x200038d4 | nvAdvMagic | g2_nvdb_adv_magic_record |
| 0x200038e4 | nvMAC | g2_nvdb_mac_record |
| 0x200038f4 | nvSCald | g2_nvdb_sensor_caldata |
| 0x20003950 | nvSCaldAG | g2_nvdb_sensor_caldata_ag |
| 0x200038d8 | nvBuzzer | g2_nvdb_buzzer_record |

- **FLAG:** our g2_uart_product_mode_state is 2 bytes, but the stock nvProdMode record is 4 bytes.
- **Result (sim13):** 0 undefined. The 0xFC43 packet is now `0143FC0669DF226531FC`, the same as stock, and the "Unmodeled EM9305 HCI opcode 0x1005" warning is gone. The rest of the HCI sequence still matches stock through advertising enable.

**LE Rand.** Not a real difference. Stock run for 8 s with em9305 logging (sim stke) also sends 4× 0x2018 from hciCoreResetSequence. The 2× seen before came from the older stock2210 run, which used a different configuration.

**Data-scan 20→21.** Not new. The extra hit is 0x5a35a5, an entry in the known 0x200002a8 code-pointer table. In sim11 one of our functions happened to sit at 0x5a35a4, which masked it.

## Batch sim14: 0x20000064 conflict and the 0x200002a8 code-pointer table (2026-10-26)

**0x20000064 conflict.** Stock _page_manager_init (0x45f15a) loads literal 0x45fa98 = 0x20000064 and passes it as both width and height to lv_obj_set_size (0x43f4c0). That value is the LVGL 9 coordinate LV_PCT(100), not a RAM address; it only happens to equal the ALS-scale cell address. The other users of 0x20000064 are fine as they are:
- the ALS code uses `audio_als_scale_active` (a real RAM cell);
- the teleprompt, onboarding, terminal-fsm and translate UIs already `#define LV_PCT_100 0x20000064`.

**Fix 17.** `app/page-manager/display_page_manager_new.c` (backup: `*.orig`) now passes the constant `0x20000064u /* LV_PCT(100) */` instead of `&audio_uart_display_page_size_cell`. The cell definition in `runtime/page-hub/display_page_hub_startup_cells.c` is now unused and left in place.

**Fix 18: initialized-data code pointers.** Backups: `bak/reloc.py.pre-codemap` and `bak/stock_ram_cells.c.pre-sim14`.
- `reloc.py` now also resolves stock thumb pointers through the `/* Stock 0xADDR ... */` comment directly above a function definition in our sources.
- **FLAGGED (positional inference):** for the PCM2.2 transition table at stock 0x200002a8, sequence N sits at index N. All 21 annotated entries agree, so the unannotated ones were mapped the same way: 0x5a20e8→seq1, 0x5a29a0→seq7, 0x5a3e80→seq22, and 0x5a40b0/2/4→seq24/25/26. In stock, those last three are single `bx lr`, matching our empty sequences 24–26.
- Newly relocated: all 27 pcm22_sequence_N entries, file_heap_reallocate (0x474d54 → audio_file_heap_realloc), and the OTA MRAM read/program/erase table at 0x200003a4 (0x5a4f30, 0x5a4f58, 0x5a4f80).
- reloc counts: code-reloc 84, code-unmapped 0 (was 22), ram-reloc 53, ram-unmapped 23, flash-word 1927.
- Note: the objects g2_stock_ram_20000290 (0x84 bytes) and g2_stock_ram_20000310 overlap at stock addresses 0x20000310..0x20000314. Both carry the same stock bytes, and no fix has been made.

**Result (sim14).** 0 undefined; **datascan 0** (was 21). The sim runs 20 s with no HardFault.

**Display (task 6).** Still no `mspi0.panel` activity in our build. Stock latches 2 frames and first reads JBD 0x9F; ours never reaches the panel driver. This is the next item to trace.

## Batch sim15–sim22 (display path, item 6)

Latest ELF: `g2/build/g2c-sim22-final-apollo-main/g2-apollo-main.elf`. It links with 0 undefined, datascan reports 0, and a 20 s run has no HardFault and no watchdog reset.

| Fix | File | Root cause → change | Evidence |
|---|---|---|---|
| 19 | hal/uart/uart-instance/instance.c | `osThreadNew` attr was raw stock flash 0x75c1ec, so the thread had a garbage name and creation stopped after uart_sync. Now uses own attr {"uart_sync_thread", cb 0x70, stack 0x1000, prio 0x2a}; log strings are now literals. | Stock bytes at 0x75c1ec and strings 0x7846d0/0x710b64/0x7846e4/0x75c1c8/0x72fa80 in stk12.bin |
| 20 | ui/lvgl/lv-heap + 3 consumers | `audio_uart_lv_heap_pool` was `.set` to raw 0x20000338, so the semaphore 0x67f050 faulted (watchdog). Consumers now bind it to `g2_stock_ram_20000338` (the pool that font_alloc initializes). | — |
| 21 | drivers/flash/nor/nor-controller-sram.c | `.set` raw 0x20074544 replaced by an own zeroed word. | Address lies past the 17752-byte stock .data image, so it is .bss in stock |
| 22 | drivers/flash/nor/nor-clock-select.c and ble/ble-radio/display_ble_radio_power_config.c | Pad-config tables read raw 0x2000006c..0x200001c8, so GPIO pins got ASCII serial bytes. New `g2_stock_ram_2000006c[87]` holds values from init_20000000.bin. 0x20074204..218 are own zeroed words (**flag**: the stock runtime writer is unknown). | init image offsets 0x6c..0x1c8 |
| 23 | display_driver_uled_options_relocated_fifteen.c | 14 raw stock Thumb addresses in the JBD4010/Hongshi option vtables are now mapped to our functions. | `apollo_main.tsv` names, e.g. 0x592f9a read_chipId |
| 24 | display_driver_uled_option_setup_pair.c | MSPI0 device-config args were raw 0x20000758/770/788/7a0, so `g2_norflash_configure_mspi_4c099c` failed and MSPI0 never initialized. They now use `g2_stock_ram_20000758[18]` (init-image values) and `g2_stock_ram_200007a0`. | Stock hook on 0x59cf1a: r2=0x20000788 → {0x201,0,0x0f000000,0x01010000,0,0} |

### Milestones

- **Threads:** all 27 threads now match stock in name and order (ui_task and displaydrv_mgr_t are new). Before this batch there were 16.
- **Display init sequence:** matches stock — uled identify → jbd setup → mspi init → configure → enable → clear → async → chipId → power_on.
- **MSPI0:** now configured, and the descriptor shape for `qspi_write_async` matches stock.
- **Display frames:** still 0 latched panel frames. In the panel model, MSPI0 never sees a transfer.

### Next lead

`display_driver_uled_packet_validate_59cb42` rejects every JBD command packet: 24 packet writes are followed by 0 encode/transfer calls. Next step is to compare it against stock 0x59cb42. That function and its callers still pass raw stock strings (0x776e5c/0x776e44), so a raw literal is a likely cause (**guess**).

### Still open

- HCI 0x1005 (Read Buffer Size) is still sent, and stock does not send it.
- The advertising name and serial use the init-image PSN "S200LDBE21…/L", while stock uses "EMU…/R". This may be caused by the nvProdMode or NVDB source (**guess**).
- nvProdMode size, the 23 RAM pointers, the 0x20000310 overlap, and items (4)/(5) are not started. Item (5) has a new class: raw code pointers in .rodata tables are invisible to datascan, so datascan needs a .rodata pass.

### Fix 25 (sim23): display frames now latch and match stock
- `packet_validate_59cb42` was already correct. Our C matches stock: it rejects NULL (line 0x98), then packet[6]==0 (0x9d), then packet[5]==0 (0xa2). A hook on our validate showed valid descriptors (handle 0x2022db54, nonzero payload), and the 4 init command blocking transfers returned 0.
- **Root cause:** `display_driver_uled_option_type0_qspi_write.c` (0x59ce1e) passed the raw stock callback `0x59c867` to the nonblocking transfer. Our image has no callback at that address, so the MSPI semaphore was never released and the frame path stalled after command 0x01. In stock, the transfer goes on to the 0x97/0xC0 transfers.
- **Evidence:** the stock symbol table (`symbols/apollo_main.tsv`) names 0x59c866 `mspi_transfer_callback`. Stock body: `*ctx=status; osSemaphoreRelease(*0x20074534)`. Our `mspi_transfer_callback` (uled_mspi_common.c) has the same body on `g2_uled_mspi_semaphore` (stock RAM 0x20074534).
- **Fix:** the raw value is replaced with `mspi_transfer_callback`. Backup: `bak/display_driver_uled_option_type0_qspi_write.c.orig`.
- **Result (sim23, 20 s):** 2 frames latched. Both have sha256 0c5cc90b079d…, the same as stock `stk12.log` frames 1 and 2. Still open: the HCI opcode 0x1005 warning, the 0x9F read fixture warning (same in stock), and the PMIC "kick while stopped" error.

### Fix 26 (sim24): .rodata/code-constant scan and RAM-literal fixes
- I confirmed with `arm-none-eabi-nm -u` that sim23 and sim24 both have **0 undefined** symbols.
- I moved `datascan.py` to `.waves/sim-fix/datascan.py` (cycle.sh now uses it). It skipped `.rodata` because this image links .rodata inside the executable `.text`.
- I added a new `.waves/sim-fix/datascan_ro.py` that scans words not covered by any function, literal pools, and movw/movt pairs for stock function addresses we don't define. It got 102 hits, and none need a fix:
  - 91 hits are in `stock_overrun_rows`, a generated fault table that copies stock data on purpose. Its header says so.
  - 6 hits are the value 0x545645, which is ASCII "EVT\0" and only looks like an address.
  - 1 movw is in `audio_ble_dm_conn_update_invalid_event_action`. It copies the stock bytes of 0x004b2df9 on purpose to reproduce stock's out-of-range table read.
  - 4 hits are integer values that only happen to look like addresses.
  - With the sim23 fix in place, the 0x59c867 callback no longer appears. This scan would have caught it.
- I added a new `.waves/sim-fix/ramscan.py` that finds movw/movt RAM constants outside all of our data and bss objects. It got 17 hits. I fixed 9, each with a citation:
  - `ownership.c` and `i2s-clock-release/clock.c`: 0x20073324 is `g_ui32ClkMgrClkSrcBm` (stock pool 0x4c43dc) and is now `g2_stock_ram_20073320+4`. The hand-copied clock code had been using memory separate from the clkmgr bodies that use the symbol, so the two kept split state.
  - `diagnostic-deinit/deinit.c`: 0x20073c08 (pool 0x57b40c) is now `g2_audio_recording_rows_20073c08`.
  - `pcm21-completion/lifecycle.c`: the field() targets 0x20056680/84/90, 0x200566a0.. and 0x200566c4 are now `g2_stock_ram_20056658+off`. In stock 0x5a1c18, r5 is set from pool 0x5a1e1c to 0x2005665c and these addresses are written as [r5+0x24/0x28/0x34/0x44../0x68].
  - The remaining 8 hits are the cm_backtrace/startup stack bounds 0x2007d000/0x2007fb00. They are correct, because our vector MSP is also 0x2007fb00.
- **sim24 (20 s):** frames 1 and 2 still have sha256 0c5cc90b079d…, the same as stock.

## Fix 27 (sim25): IOM bContinue read as word -> PMIC "kick while stopped"
- Root cause: `display_ble_hci_vendor_{receive,send}.c` read `option=get(descriptor+32u)` (32-bit). Stock reads a byte: `ldrb.w r0,[r4,#32]` at 0x55cc92 (am_hal_iom_blocking_transfer) and `ldrb.w r0,[r9,#32]` at 0x55cfb4. Byte +34 is the priority (=1), so the word was nonzero and CONT (CMD bit7) was set on every transfer (ours CMD 0x281/0x182 vs stock 0x201/0x102).
- Effect: all nPM1300 I2C reads returned 0 -> soc=0 -> EnterShipMode (0xb02) every second -> "kick while stopped".
- Fix: `option=descriptor[32u]` (both files, backed up).
- sim25: 0 'kick while stopped', 0 errors/faults (sim24 had 1), frames 1+2 sha256 0c5cc90b… = stock, `nm -u` = 0.
- Still open: HCI opcode 0x1005 (Read_Buffer_Size) is not modeled in the em9305 sim.

## Fix 27 verification + Fix 28 (sim26) + Fix 29 (sim27)
**PMIC verified vs stock (15 s runs, `LogPeripheralAccess iom7`):** IOM7 CMD (0x120) write sequence is byte-identical to stock (302 writes). The 134 FifoPop values match stock except one (#7: stock 0xC2, ours 0x80C2). This is probably caused by the upper TX-buffer bytes our callers push, e.g. FifoPush 0x82B80905 vs stock 0x905. The push loop is the same as stock (`ldr r1,[r4]` at 0x55ce92), so the difference is in the caller's TX buffer (**guess**, not fixed). `g2_charger_telemetry` reads [0,31,3798,0,2500], the same as stock (hook on device_mgr_fn_004c6990).

**Word-vs-byte sweep:** every `get(descriptor+N)` in the codebase is in the two IOM files. In `display_ble_hci_vendor_send.c`, `type=get(descriptor+20u)` became `descriptor[20u]`, citing stock `ldrb.w r0,[r9,#20]` at 0x55cfae. All other fields are word loads in stock (ldr/ldrd at 0x55cf9c..0x55cfca), so they stay.

**Fix 28 (opcode 0x1005):** `HciReadBufSizeCmd`'s stock body (0x52b620) sends **0x1001**: `movw r0,#4097; bl hciCmdAlloc 0x52ae38; bl hciCmdSend 0x52ae5e`. The tsv name is misleading. Our alias linked Cordio's real HciReadBufSizeCmd (0x1005). The only caller is `display_ble_hci_driver_handler.c`, which now uses a local static that sends 0x1001. Evidence: hciCmdAlloc hook, stock lr=0x52b62d op 0x1001, ours lr in HciReadBufSizeCmd op 0x1005.

**Fix 29 (serial source = PWRCTRL periph enum order):** SVC_ReadPSNFromOTP stopped after 1 word because am_hal_infoc_read_word returned 7: DEVPWRSTATUS bit27 (OTP) was off. Stock's `am_hal_pwrctrl_peripheral_control` (0x6becb0, via pool 0x47f944) puts IOSFD0 and IOSFD1 at index 1 and 2. Upstream puts them after OTP, so every index from 1 to 0x1d was shifted by 2. Decompiled callers that pass stock numbers (0x1d OTP, 0x17 CRYPTO, 0x14 GFX, IOM 3+n…) were powering the wrong blocks, and pwrctrl's own CRYPTO and GFX special cases used the upstream numbers. Stock evidence: `cmp r0,#23` at 0x47f5e0 and `cmp r0,#20` at 0x47f5fe.
- Fix: add `G2_STOCK_PWRCTRL_ORDER` #ifdef blocks to `third-party/.../hal/am_hal_pwrctrl.h` (the enum) and `am_hal_pwrctrl.c` (the table), with the citation. Add `-DG2_STOCK_PWRCTRL_ORDER` to all 42 `g2-apollo-main-*` profiles in `g2/src/sources.json`. Bootloader, em9305 and other targets are unchanged. Backups are in bak/*.orig.
- sim27: OTP is read (8 slots). The advertising PSN is now stock's "S2EMU…" (HCI packet 0x2008 byte-identical to stock). HCI host-packet stream = stock except one byte. 0 faults/errors, frames 1+2 = stock sha256, `nm -u` = 0.

**Open:**
- Scan-response name side 'L' vs stock 'R' (`Even G2_32_L_…`). The side is not taken from the PSN. Its source is next.
- 0x20074204 words, nvProdMode size, the 23 RAM pointers and the 0x20000310 overlap, the 264 unclassified uses, and the 278 flash addresses have not been started.
- Flag: bootloader HAL TUs still use the upstream enum. Not checked against the stock bootloader.

## Enum-order audit, FIFO #7, Fix 30 (sim28)

- Bootloader PWRCTRL: all stock bootloader versions use stock order (IOM0 = idx 3); our bootloader compiles no upstream HAL / no PWRCTRL enum, so no change needed.
- Interrupt vectors: all 130 slots map to the same stock functions. All 20 upstream HAL const tables found byte-identical in stock. clkmgr/stimer IDs consistent (HFRC=4, LFRC=0, MAX=7). GPIO enums NOT specifically audited (open).
- FIFO read #7 (nPM1300 0x6B, 10 B from 0x0511): byte 1 (NTC MSB 0x0512) 0x80 ours vs 0x00 stock. TX bytes masked to length identical (201 pushes), CMD sequence identical; difference attributed to emulator ADC timing (GUESS). Telemetry matches stock; not fixed.
- **Fix 30 (L/R side):** `audio_uart_device_role_cell` (role_display_runtime_cells.c) and `g2_audio_service_mode` (service_mode_state.c) were two separate objects both for stock 0x20075024 (linked 0x20003a00 vs 0x200039ff), so role_get wrote one and the adv-name getter read the other (always 0 -> 'L'). Now the role cell is an alias of `g2_audio_service_mode`. Evidence: stock role_get 0x45a578 strb @0x45a6c8 via pool 0x45b0f4 = 0x20075024. sim28: nm -u 0; watchpoint on 0x200039ff shows write pc=0x44abf8 (in audio_uart_role_get) v=1 (= R), same as stock (pc 0x45a6c8 v=1).

### Fix 30 confirmation
sim28 scan response (HCI 0x2009) is byte-identical to stock: `Even G2_32_R_22DF69` (sim27 had `_L_`). Adv data (0x2008) identical.

## Fix 31: duplicate objects for one stock RAM cell (sim29, sim30)
New tool `.waves/sim-fix/dupscan.py ELF`: collects `.g2_ram_ADDR` sections and declaration comments naming 0x2007xxxx, maps names to linked addresses, and reports stock cells backed by >1 linked object.
Initial scan: 17 distinct stock cells (section scan 6 + comment scan 14, 3 overlapping). Merged by keeping one definition and defining the others as `alias` in the same TU (citations are stock literal-pool words holding the address):
- 0x200744e4 g2_display_queue <- audio_uart_input_queue (pool 0x4443c4/0x4448a4)
- 0x200744e8 audio_uart_display_mutex <- audio_uart_input_mutex, g2_display_sender_mutex (0x4443c8/0x4448a0; stock 0x444720 creates the mutex here)
- 0x200749c4 g2_uart_tinyframe <- g2_uart_sync_module (0x45dd64/0x45ebdc)
- 0x200749cc g2_uart_send_queue <- audio_uart_sync_schedule_queue, audio_settings_peer_send_queue (0x45d068/0x45ebc8/0x4651c0)
- 0x200749d4 audio_uart_sync_timer_sem <- g2_uart_sync_semaphore (0x45dd38)
- 0x20074b10 audio_uart_sync_timer_event <- audio_uart_input_event_flags, g2_uart_thread_event, audio_settings_peer_event (0x45d0c8/0x45df14/0x465470)
- 0x2007433c audio_ble_cached_conn_params <- audio_ble_msgtx_mode (0x477ab0/0x478700)
- 0x200744ec display_driver_enabled <- audio_display_hw_initialized_200744ec (0x4744a8)
- 0x20074544 audio_uart_font_flash_device <- g2_norflash_controller_handle_20074544 (0x470014/0x4708a4/0x4710ac). With the merge, the flash power calls (stock 0x4c26e0) take the real MSPI handle and follow stock's sleep/wake pattern (sim: 8386 calls vs stock 8053, same (2,1)/(0,1) alternation)
- 0x200746bc audio_uart_display_lock <- display_buffer_semaphore (0x47390c)
- 0x200746e0 audio_uart_ring_secondary_head_cell <- audio_system_alert_font_200746e0 (0x463bf0/0x469ba0/0x46b08c)
- 0x20074aa0/0x20074aa4/0x20075031 audio_uart_timeout_{queue,mutex,running_state} <- audio_uart_pool_{queue,mutex,initialized} (0x491618/0x491650/0x491630)
Not yet merged (struct/array cells, size check needed): 0x200727f0 (audio_ble_controller/audio_ble_comm_state), 0x20073b30 (audio_charger_state/audio_charge_sync_record), 0x20073b90 (audio_uart_ble_logger_descriptor/g2_elog_sink).

Results: nm -u 0. sim29 (first 6 groups only): xTaskPriorityDisinherit wrote to 0xFFFFFFFF because g2_display_sender_mutex was still separate; sim30 fixes that. The display queue, mutex and GPU path are now live: the GPU ring-stop warning now appears as in stock, and frames match stock.
**REGRESSION (sim29 and sim30), fixed by Fix 32 below:** a WDT reset ("Watchog reset triggered") within 20 s; stock stkp at 20 s has none. Before Fix 31 these paths ran on NULL handles and did nothing. The cause is not yet isolated. Next step: hook am_hal_wdt_restart LR timeline, ours vs stock.

## Fix 32: TinyFrame timeout-listener argument (sim38), the root cause of the Fix 31 WDT reset
Bisect (sim31-37, each un-merging one alias from the sim29 groups, run in parallel at 20 s):
| variant | un-merged | WDT |
|---|---|---|
| sim31 | audio_uart_input_queue | yes |
| sim32 | audio_uart_input_mutex | yes |
| sim33 | g2_uart_sync_module (0x200749c4) | **no** |
| sim34 | audio_uart_sync_schedule_queue | yes |
| sim35 | g2_uart_sync_semaphore (0x200749d4) | **no** |
| sim36 | audio_uart_input_event_flags | yes |
| sim37 | g2_uart_thread_event (0x20074b10) | **no** |
Breaking any one of the three sync-framework cells disables the UART sync path, so the hang only appears once the merges make that path live.
Root cause:
- WDT kicks (am_hal_wdt_restart) come only from prvIdleTask and tickless sleep.
- xTaskIncrementTick sampling: `worker_thread` takes 287 of 292 samples in sim30, against near-idle in sim33.
- Worker-dispatch hook (0x45d354): 72,890 items, all `{audio_uart_timeout_dispatch, opaque=audio_uart_send_end4, status=-2}`. `send_end4` was entered with r1 = itself and resubmitted itself forever.
- First entry was from TF_Tick with r1 = garbage (the fn pointer left in r1). Upstream calls `lst->fn_timeout(tf)` with one argument.
- Stock TF_Tick 0x492288 does `ldr r1,[r6,#20]; movs r0,r4; ldr r2,[r6,#8]; blx r2` (0x4922ae-0x4922b4), i.e. `fn_timeout(tf, lst->userdata2)`. A stock sim hook on 0x45d710 sees 14 calls, lr=0x4922b7, r1=0, which is a no-op.
- Our TF_IdListener layout matches (fn_timeout +8, timeout +12, userdata2 +20; parser ticks tf+18).
Fix: `third-party/upstream/tinyframe/TinyFrame.c` gets an `#ifdef G2_STOCK_TF_TIMEOUT_ARG` call passing `lst->userdata2`. The define is added to all 42 g2-apollo-main profiles in sources.json. Our TF_Tick now emits `ldr r1,[r7,#20]; mov r0,r4; blx r2`.
sim38: nm -u 0. No WDT, no fault. The WARNING set equals stock (GPU ring-stop + JBD 0x9F only), frames match, and the scan response is `Even G2_32_R_22DF69`.
New tools: .waves/sim-fix/variant.sh (un-merge-and-build for bisects; restores sources after the build).

## Fix 33 — merged split stock RAM objects (sim39)
- 0x200727f0: `audio_ble_comm_state` is now an alias of `audio_ble_controller` (stock pool 0x4b81fc, users bleDmCback 0x4b74e0, bleProcMsg 0x4b7c8e, bleCommHandlerInit 0x4b7e78).
- 0x20073b30: `audio_charger_state` grows to 0x18 bytes (stock `movs r1,#24; ldr r4,=0x20073b30; bl memset` at 0x4ad016); `audio_charge_sync_record` is aliased onto it (pool 0x4ad908, CHG_* users).
- 0x20073b90: `g2_elog_sink[8]` is aliased onto `audio_uart_ble_logger_descriptor` (pool 0x448fcc; setters 0x448c74/0x448cb8, transport 0x448dd2).
- sim39: 2870/2870 compiled, 0 duplicate strong symbols, 0 undefined. 20 s run: no WDT and no fault; the warning set is the same as sim38 (gpu ring-stop, panel 0x9F).

## Fix 34 — nvProdMode record size and init (sim40)
- `g2_uart_product_mode_state` is now 4 bytes with init {1,0,0,0}. Evidence: stock FlashDB KV table at 0x20003868, entry 2 = {0x78bfb4, 0x200038f0, 4}; stock init image +0x38f0 = 01000000. The old 1-byte object let the 4-byte KV load overrun into `g2_uart_sync_module`. The other 8 NVDB records already matched stock in size and init.

## Vendor-lib audit results
- Matcher v3 (prefix-based library detection, movw/movt-paired constants, string anchors, callee voting, 1:1 matching). Mapped: lvgl 424/2299, U7 52, littlefs 81, nanopb 27, ambiqhal 95.
- None of the candidates is a real divergence: elog_strcpy (codegen), lfs_file_flush (memcpy vs inline), inv_imu_flush_fifo (mismatched; stock 0x47243a is app code), npmx (matcher off by one), tlsf (0xc74 same), prvHeapInit (0x2f000 same), attsIsHashableAttr, lv_draw_ambiq_fill (0x4000501 built with orr), TinyFrame layout.
- Cordio: constants differ by about 3 in `__LINE__` values, which points to a source-revision difference. Not fixed (GUESS).
- am_hal_gpio_pinconfig: equivalent (PADKEY 0x73, capability bitmaps identical).
- Checked with objdump, not Ghidra.

## 0x20074204..0x20074218
- Stock reads these 6 words only at 0x4c2c3e..0x4c2d38, as pinconfig args for pins 27/33/36/49/63/24. They sit past the 0x4558-byte .data image, in zeroed .bss. No stock pool word points into them other than the one table. Our zeroed array matches. Closed; a base+offset writer elsewhere is not fully ruled out (GUESS, low risk).
- sim40 (Fix 33+34): 2870/2870 compiled, 0 duplicate strong symbols, 0 undefined. nvProdMode is at 0x20007480 (4 B) and g2_uart_sync_module moves to 0x20007484, so the overlap is gone. 20 s run: no WDT and no fault; the warning set is the same as sim39.

## Sim verification (sim38–41, 2026-10-27)
Each run's log spans 20 s (first..last line), with advertising enabled (`010A200101`) once and 2 frames latched. Executed instructions are 0x4DD18C9 vs 0x520DFF3 for stock. `emulation RunFor "20"` is virtual time, so cycle.sh needs no fix.

## Fixes 35–41 (sim44: 2870/2870 compiled, links with 0 undefined, 20 s run, advertising enabled, 2 frames latched)
- **35** Removed `g2_stock_ram_20000310`. It had no users, and the range overlaps words 32–33 of `g2_stock_ram_20000290` plus `g2_stimer_last_compare_20000318` (stock 0x48d68c).
- **36** 4bpp framebuffers get their real sizes: `g2_stock_ram_20080000` [0x14400] and `g2_stock_ram_20094400` [0x25820] (GUESS beyond 0x25807). The MPU limits now use `W()`, and the 0xc20 record points at `g2_i2c_iom_nb_txn_buffer`.
- **37** The display ring font descriptors now point at 5 real lv_font_t objects (stock init values). Their dsc words are still raw flash addresses (OPEN, flash list).
- **38** The log ring state is initialised to {storage, 0x8000, 0, 0} (stock init +0x4c8). Before this, `audio_log_emit` memcpy'd to address 0.
- **39** Pools get their real sizes: `g2_stock_ram_20279670` [0x2d000] and the elog pool `g2_stock_ram_202d3fc8` [0x11000]. `g2_elog_dummy_node` is now an alias of pool node 255 (+0x10ef0, stock 0x4489e8 / word 0x448fb4), defined in stock_ram_cells.c.
- **40** codec-host irq.c, request.c and lifecycle.c used the raw address 0x20000d2c. They now use `g2_uart_channels`. Evidence: a hook on am_hal_uart_power_control showed the call from LR 0x53ac0b (`codec_channel_disable` inside `uart_channels_init_55e388`) passing handles 5, 0 and 0x2020000, because it read our layout at the stock address. This removes the sim41 warning "ReadDoubleWord ... 0x2020000" (PC 0x60FA04).
- **41** Two layout changes:
  - FreeRTOS `ucHeap` (0x2f000) moves to DTCM via `.dtcm_heap (NOLOAD)` in the .ld. Stock has an unowned 0x2f001 span at 0x20004557 (GUESS on base).
  - The capped objects shrink to their stock spans: 2003fa98 [0x5a00], 203195e0 [0x6004], 20367bd8 [0x1220], 20378d98 [0xc08], the last kept at the MPU region 8 limit (owner OPEN).
- **OPEN** `g2_stock_ram_2013be70` (LVGL pool, real size 0xcd000) stays at 0x10000. At full size SSRAM overflows by 170140 B, yet pool_initialize still gets 0xcd000, so the TLSF tail overruns. Needs a RAM rebalance (DTCM has about 0x21a40 free after ucHeap).

### List status
- 23 RAM pointer words: all classified (4 fixed in Fix 36; 19 are dead copies, owned elsewhere, or byte tables). The 0x20000310 overlap is closed (Fix 35).
- Unclassified uses (rawscan, 277 literals): classified. About 180 are not addresses. Live raw addresses fixed so far: 0x20000d2c (Fix 40). Remaining live ones: 0x20004488 lconv, uled 0x200523d8 (no owner), radio_record 0x20074958–64 / 0x200036dc, 0x2034bc10 OTA cache, the sysctrl G_* macros (10), tracepoint 0x200043f8/40/b0, pending.c trims 0x2000453a–f, stop.c ctx[10], display_font_alloc MPU 0x2013be70/0x20378d9c, and ble_hci compare 0x20080000 (bound check, judge).
- 278 flash addresses: not started.

## Fixes 42–43: LVGL pool at its real size (sim48: 2870/2870 compiled, links with 0 undefined, 20 s run, advertising enabled, 2 frames latched, only the 2 warnings already seen in sim40)
- **Cause of the overflow.** Stock SSRAM fits. Ours didn't, for two reasons:
  - (a) Blob cells inflated by plan.py ranges. Each spanned stock objects that we also define by name, so that memory was allocated twice.
  - (b) Every zero-init object went to SSRAM, including ones stock keeps in DTCM.
- **42** Use-derived sizes:

  | Object | Old | New | Evidence |
  |---|---|---|---|
  | 20056658 | 0xf3b8 | 0x70 | max access `data[26]` at +0x6c, stock 0x5a4d48 |
  | 20071ea0 | 0xf08 | 0x70 | static TCB |
  | 200704e8 | 0xe80 | 0x104 | +4 rx buffer, length checked >0x100 |
  | 20073488 | 0x430 | 0x34 | memset(+4, 0x30) |
  | 20071988 | 0x518 | 0x40 | no users |
  | 20102c38 | 0x3e48 | 0x1c | no users |
  | 2003fa98 | 0x5a00 | 0x4000 | stack depth 4096 words |

  - **New `.dtcm_bss`** (zeroed by a new row in the g2c_gnu_init.c region table). It collects `.bss.*_2000xxxx..2007xxxx` plus the 396 objects that live in DTCM on stock but carry no address suffix, listed in the generated `link/g2-dtcm-bss.ld` from the reloc map.
  - **`g2_stock_ram_2013be70` is now [0xcd000].** Citation: `audio_uart_heap_initialize_4842e6` (display_font_alloc.c) passes `pool_initialize(..., 2013be70, 0xcd000)`, and the MPU region 6 limit is 0x20208e6f = base + 0xccfff.
  - **Layout:** DTCM ends at 0x200710f0 (stack at 0x2007d000). SSRAM ends at 0x2037cd0c, vs stock zero-init end 0x2037CE44.
- **43** MPU region 8 owner is `display_driver_uled_work_buffer` (stock 0x203795a0..0x2037999f, 0x400 B), and the record now points at it. `g2_stock_ram_20378d98` is 0x404 (small pool at +4, 0x400 B). The `secondary` and `small` records in display_font_alloc.c no longer use raw addresses 0x2013be70/0x20208e6f/0x20378d9c/0x2037919b; they use the owning objects.

## Fixes 44–48 (sim53: 2870/2870 compiled, links with 0 undefined, 20 s run, advertising enabled, 2 frames latched, only the 2 warnings already seen in sim40)
- **Blob re-audit.** About 0x2b74 B of double allocation is left in small blobs; it's harmless for space. The real problem was accesses: 49 `blob+offset` uses (`/tmp/blobuse.py`) landed on a different stock object, so they touched a stale copy.
- **44** Rewrote the 48 cross-object uses to owner+offset, e.g. pcm21 control/completion `20000240+0x54` → `20000290+4`, request.c `200738b8+0xe4` → `20073998+4`, clock_requests `20074000+0xec` → `200740e8+4`, and 30 initialisers in stock_ram_cells.c that point into named objects. The `g2_elog_dummy_node` alias was kept on purpose.
- **45** 43 live raw RAM addresses now use their owners (owner.py):
  - lconv 0x20004488 in ring-locale and float_render
  - radio_record slots (20074948+0x10..0x1c) and log argument (200036d8+4)
  - OTA cache 0x2034bc10 → `g2_ota_cache_buffer`
  - the 10 sysctrl `G_*` macros
  - tracepoint stdout/stderr
  - the pending.c ton trims
  - stop.c `ctx[10]`
- **46** uled `MSPI_STATE_BASE` 0x200523d8 → `g_MSPIState`. Evidence: 4 × the 0x8d0 stride = our 0x2340 B, which matches Ambiq's `g_MSPIState[4]`. The tracepoint `0x200043b0` (IAR stdin FILE, no owner in this build) compare was dropped with a comment.
- **Classified, not changed:** `DEVCFG` (already relocated; scanner false positive), and the vendor_stack_config `<0x20080000` compare (DTCM/SSRAM bound).
- **47** 231 cast stock-flash string pointers in 36 files are now C string literals taken from the stock image (`stk12.bin`, base 0x438000), each tagged `/* stock 0xADDR */`. Before, they read whatever bytes our image had at the stock address, including format strings.
- **48** 11 data reads now use const objects built from stock image bytes:

  | Address | Contents |
  |---|---|
  | 0x78de24 | uled LDO config (2 words) |
  | 0x78ee40, 0x78ee48 | pin config words |
  | 0x76b12c, 0x76b148, 0x76b164 | 28 B MSPI templates |
  | 0x78eda4 | quicklist 8 B packet |
  | 0x5232d0 (+0x18 view) | nema arc float table, 13 words; word 0 (=0x20074efc, a literal-pool word) is never indexed |
  | 0x753dbc | string |
  | 0x756108 | → `audio_uart_image_class_756108` |

  The cast-based flash scan (`.waves/sim-fix/flashscan.py`) now reports 0 sites.
- **OPEN, new and larger: bare flash words in initialisers.** 2059 `0x004xxxxx`–`0x007xxxxx` literals in 21 files: 1927 in stock_ram_cells.c, 102 in fault_lookup_overrun, and 5 font dsc in the ring descriptors (Fix 37). There are 1791 distinct addresses, 1209 of them matching a symbol with a stock-address suffix. These are stock-image pointers (functions, strings, tables) copied into RAM init data. They need a reloc pass (Thumb bit, non-pointer constants, unnamed strings).

## Fix 49 — bare stock flash words → symbol refs (sim55)

Tooling: `.waves/sim-fix/flashreloc_scan.py` (classifies with readelf symbol *type*, not nm letter —
nm reports `.text`-resident image descriptors as `T` though they are STT_OBJECT) and
`.waves/sim-fix/flashreloc_apply.py`. Backups: `.waves/sim-fix/bak/*.pre-fix49.orig`.

Of 2059 words: SYM 1399, FUNC 62, INOBJ 18, STR 434, UNRES 145, FUNC_EVEN 1.

* Applied 1479: `stock_ram_cells.c` 1476 (`W(sym,off)` / `F(sym)`, 1205 new externs),
  `terminal_row_children_5ea2b0.c` 3 (asset returns 0x7733a8/0x770890/0x773258).
  Evidence: value is the exact stock address of the named object/function (name suffix = stock address);
  FUNC literals are odd = function+1, ABS32 against STT_FUNC re-applies the T bit (verified in ELF:
  attsProcReadMultiVarReq word reads 0x0050a51d).
* Skipped, constant look-alike: 0x00480008 in `pb_descriptors_data.c` (nanopb field-info word, cf.
  neighbour 0x00140008); 10 UNRES words landing mid-instruction in Thumb code (0x5c0004, 0x4c072d, 0x4b2df9,
  0x44000c, 0x5c000c, 0x5d002b, 0x4e0002×3, 0x69b077); 0x438000 in `iar_cmain.c` (image base, identical in ours).
* Deliberately left: 81 words in `fault_lookup_overrun_509b48.c` rows 43..255 (faithful replica of stock's
  out-of-bounds read of unrelated data, per file header).
* Open: STR 434 (to become const string objects); ~52 UNRES pointing at unnamed stock flash data
  (ring font dscs 0x77f3xx/0x77f4xx, lv_font at 0x755610, CRLF CLI strings 0x6bf5xx, image-dsc runs 0x76c0xx,
  unnamed code 0x55f3xx). These need objects recovered from stock bytes first.

sim55: links (0 undefined in link.log; build summary "24 unresolved: ok (composed)" — GUESS: same composed
set as prior runs, not re-diffed), 20 s span, `010A200101` advertising once, 2 frames latched, only the 2 known
warnings (GPU ring-stop, JBD 0x9F).

## Fix 50 — flash-word relink pass, part 2 (sim56/sim57)

All targets link with 0 undefined references. em9305 is still built at -Os. sim57 ran 20 s of virtual time (04:47:02→04:47:22), advertised `010A200101` once, latched 2 frames, and logged only the 2 known warnings (GPU ring-stop, JBD 0x9F).

- **STR, 400 words** in stock_ram_cells.c are now C string literals copied byte-for-byte from stk12, each tagged `/* stock 0xADDR */` (`.waves/sim-fix/str_apply.py`). This includes the short ones: weekday names at 0x78f130.., CLI command names at 0x78f330.., and the list at 0x755364. Strings in wsf-trace.c, extended-log-smp-format.c (now `streq`) and the locale "C" prefix were also converted.
- **Fonts:** 5 ring fonts (dsc 0x77f374/414/428/464/478) were recovered from stock into rom_fonts_data.c (`fontx.py`), with 0 bitmap-index mismatches. The display descriptors now point at them. lv_property default 0x5a now uses `lv_font_montserrat_14` (stock 0x755610).
- **SYM, 14 words:** I2C pin tables 0x786020..050 and attc disc chars 0x78df94..dfdc are aliased or created in ble_app_data.c and peripherals_data.c. Config words attCfg, smpCfg and appReqActCfg are now symbolic.
- **Tables:** `g2_flash_tbl_7097e4/824/864/8a4` are const copies of stock bytes.
- **Left raw, with evidence comments at the cell:**
  - kb_map/kb_ctrl shadow (stock RAM 0x20002b9c): its only stock user is lv_keyboard, and our LVGL uses its own statics.
  - Ops table 0x55f3xx (stock RAM 0x20002e0c): its only users are in the unported range 0x55e99c..0x55f74c.
  - 0x620063: a packed config constant (GUESS on the field name).
  - 0x444444 (colour), pb field-info words, the image base, and 10 mid-instruction look-alikes.
  - fault_lookup rows 43..255 (81 UNRES + 21 STR): a faithful copy of stock's overrun.
- **Unresolved count:** sim53 and sim57 both report 24 composed unresolved (1421 before aliases), and neither final ELF has any UND symbols. report.json records only the count, not the names, so I have not checked the names one by one (UNVERIFIED).
- Process fix: flashreloc_apply.py now puts its cell externs after `#define F(`, which fixes the sim54-style ordering bug.

## Fix 51 — leftover flash words, coverage map, 120 s input run (sim58, in58 vs instk)

- **Leftover flash words** (`flashreloc_scan.py` on the sim57 ELF; 141 words): 81 UNRES + 21 STR are the fault_lookup overrun, already justified. 22 stock_ram_cells UNRES are the kb_map/kb_ctrl shadow and the npmx ADC ops table, both with comments. The INOBJ is 0x620063 (constant). The rest are constants in context: nanopb field info (`0x780008`, `0x480008`, `0x44000c`, `0x5c000c`, `0x5c0004`), colour 0x444444 ×2, image header w/h `0x5d002b` ×2, VTOR base 0x438000, NEMA command words `0x4e0002` ×3, and a storage hash word `0x69b077`. `0x4b2df9` in the dm_conn_update table is a faithful stock byte-table overrun that is read as data.
  - **One live bug fixed:** `display_driver_uled_transfer_async.c` passed raw stock `0x004c072d` as the MSPI callback, which would branch into unrelated code. It now passes `mspi_dummy_callback` (stock 0x4c072c, AmbiqSuite am_hal_mspi.c). The backup is `*.pre-fix51.orig`.
- **Unresolved names:** the 24 composed unresolved symbols (`report.json` → `compose.undefined`) are identical in sim53 and sim57/58: linker-script symbols (`__bss_*`, `__data_*`, `__dtcm_bss_*`, `__start/__stop_kvdb_migration`, `_estack`, `_etext`, `_sstack`, `_stext`), `g2_iar_fputc_weak`, `g2_iar_putchar_select_a/b`, and 8 `nrf_fuel_gauge_*` (a prebuilt library). The final ELF has 0 UND symbols.
- **Coverage map:** see `g2/docs/apollo-coverage-map.md`. 6,890 of 8,844 stock functions are matched. The 298,700 unmatched bytes are mostly unnamed library internals; there are 0 raw live stock-code pointers, 0 undefined symbols, and 0 stubs (the only `bx lr`-style match, `silent_mode_refresh_callback`, is equivalent: stock returns 1 on every path). Strings absent from our image are LVGL/littlefs assert text or log text our port rewords. My earlier label of 0x55e99c..0x55f74c as "unported" was wrong: it is the stock npmx driver, which we build from upstream source (`npmx_adc_*` 0x5b5c6c..). I corrected the cell comment. Nothing reachable needed porting.
- **sim58** (20 s cycle): 0 undefined, adv once, 2 frames latched, only the 2 known warnings.
- **120 s input scenario** (`.waves/sim-fix/inputsim.sh`), same script on our sim58 and on stock stk12:

| step | ours (in58) | stock (instk) |
|---|---|---|
| fault status at 20 s / 120 s (CFSR, HFSR) | 0 / 0 | 0 / 0 |
| `ConnectPeer 24 0 500` → handle | 1 | 1 |
| first ATT from device | `02 f700` (MTU req 247) | same |
| ATT Read handle 3 | `0b` "Even G2_32_R_22DF69" | same |
| Read By Type 0x2a00 | `09 15 0300` "Even G2_32_R_22DF69" | same |
| later L2CAP signalling | conn param update req int 72..84, lat 4, to 600 | same |
| em9305 protocol errors / peer errors | 0 / 0 | 0 / 0 |
| adv `010A200101` / frames latched / warnings | 1 / 2 / the 2 known | same |
| instructions at 20 s / 120 s | 72.7 M / 115.1 M | 86.1 M / 129.6 M |

  Every BLE byte matches stock. The instruction-count difference is idle-loop time (both PCs sit in their idle paths), not a behaviour difference.
  - **Touch: UNVERIFIED.** `iom5.touch PublishTouchFrameHex` succeeds, but in this single-machine platform the touch attention line is not routed to GPIO27 (`foreground_gestures.py` patches `Attention -> gpio@27` in for its own scenario). Neither image reacts, so this run does not test touch. EvenHub messages were not sent: they need the encrypted, paired link (`pair_renode_link` in tests).

## Fix 52: paired session, touch, and EvenHub SDK handshake vs stock (hubstk/hubstk2 vs hub58/hub58b)

Driver: `.waves/sim-fix/hub/hubsim.py <bin> <run>`. SDK frames come from `.waves/sim-fix/hub/adapter.ts`, which imports `evenhub/src` encoders and decoders read-only.
Scenario: boot 20 s, connect, MTU 247, LE Secure Connections pairing, discover EUS and enable its CCC, write each SDK step, then publish 5 touch frames.

- **GPIO27:** the base `platforms/g2-apollo510.repl:157` already routes touch `Attention -> gpio@27`. The Fix 51 note "attention not wired" was wrong; no patch is needed.
- **Pairing and encryption:** identical. SMP completes on both, `EncryptedConnectionCount=1`, and the SMP bytes match. Both send the post-pairing GATT discovery `060100ffff00280118`; ours sends it slightly later, after SecAuth rather than during pairing (timing only).
- **GATT:** identical. EUS service 5450 has write 0x0842 and notify 0x0844 (CCC 0x0845). Service 1001 is at 0x0820, 6450 at 0x0860 and 7450 at 0x0880.
- **SDK responses:** identical payloads on both (only syncIds differ, and those are free-running).
  - SecAuth reply: service 0x80, cmd 4, magic 0x41 echoed, tag 3, empty body.
  - After SecAuth and after TimeSync, the glasses send unsolicited 0x80 cmd 4 frames with flags 0x01, magic equal to their own syncId, and body {1:1}.
  - PipeRole x2, SettingStatus (0x09), heartbeat, CreatePage (0xE0) and Image: **no reply on either image**. All ATT writes are acknowledged (0x13).
- **Touch: REGRESSION in ours.**
  - Stock reads every published frame within 50 ms: attention returns high and `ReportPending=False`, for all 5 frames.
  - Ours never reads the first frame, even after 3 s: attention stays low and the report stays pending, so the model refuses the next 4 publishes.
  - Neither image sent any BLE notification for a gesture.
- **Health:** 0 faults (CFSR/HFSR 0) and 0 protocol errors on both.

SDK assumptions:

| Assumption | Result |
|---|---|
| SecAuth reply echoes magic | **Confirmed** (0x41) |
| devcfg service 0x80 | **Confirmed** |
| PipeRole / TimeSync replies echo magic | **Not observed.** No reply to PipeRole. TimeSync is followed only by the unsolicited 0x80 frame, whose magic is not ours (guess: an async status/ack push) |
| TimeSync field 3 compat int64(-24) | **Tolerated** (no fault, no error), but nothing confirms it is used |
| Setting status: version in fields 5/6 | **Untestable.** No 0x09 reply on either image (guess: setting service needs the second-arm/peer pipe or app state the sim lacks) |
| EvenHub service 0xE0, create result / ImageStatus | **Untestable.** No 0xE0 reply on either image (guess: same gating) |

Next: find why our GPIO27 touch-attention path never runs a read (check the GPIO27 interrupt config and handler registration vs stock).

## Fix 53 — touch regression (sim59)
- Root cause: `input_msg_send_record.c` used a private `audio_input_message_state[16]` (0x20003a17, never written) in place of the input thread descriptor stock reads at RAM 0x2000408c (+8 thread, +12 queue). So queue==0 and every touch send was dropped.
- Fix: alias it to `g2_input_thread_desc` (thread_input.c). Evidence: touchtrace hook counts; hub59 reads all 5 frames within 50 ms with 0 faults, the same as stk12.
- Follow-up: `.waves/sim-fix/ramdup_candidates.txt` lists other `.g2_ram_*` sections whose address another file also documents. These may have the same duplicate-object bug and have not been triaged.

## Why 0x09 / 0xE0 need the peer arm (code path)
- `TPL_Init` (thread_manager.c:179): frames with header[7] bit 0x20 (sync) go to `audio_ble_send_status_message` (0x464d1c). It queues a kind-1 node on `g2_uart_send_queue`. `SyncModuleSendDataHandler` sends a TinyFrame over UART0 to the other arm, with timeout 0x32. Only on the peer's 0x0a ack does `audio_uart_user_response` dispatch the frame locally.
- So with a single arm, 0x09 and 0xE0 are never answered. With paired stock (`hubpstk`), every step is answered: PipeRole ×2 echo, settings cmd2 with versions in fields 5/6 = "2.2.6.10", heartbeat, CreatePage code 0, and image status 4.
- SDK assumptions confirmed: service 0xE0, version fields 5/6, magic echoes. TimeSync field 3 is tolerated but never echoed.

## Fix 54 — UART0 sync config (sim60)
- Root cause: `g2_uart_sync_buffer` (stock .data 0x20000d9c, passed to am_hal_uart_configure 0x58e09e via 0x584bc0) was zero BSS in ours. That gave baud 0 and 5-bit words, which caused about 250 "5-bit word length" warnings when paired.
- Evidence: stk12 under Renode at t=3 s reads 0x000E1000 0x00000203 0x02020000 0x00000000. It is now initialized to those values.
- Result: hubp60 has 0 five-bit warnings. Still open: paired ours only sends the 0x80 cmd4 frames, with no PipeRole, 0x09 or 0xE0 replies. Next suspect is the peer TinyFrame exchange: the listener, the uart_thread_handler path, or RX callback 0x5417a5.
- Hooked paired run hkp60 vs hkpstk: in ours the link works (rxcb/TF_Accept/resp fire on both arms), so Fix 54 is necessary but not sufficient.

## Fix 55 — peer user-data handler arguments (sim61)
- `audio_uart_user_broadcast` (stock 0x442524 find_ui_DataHandler_by_id) called the registered handler with flags only. Stock 0x44254e..0x44255a passes r0=uxth(flags), keeps r1=payload and r2=length, then blx row+4. Ours handed the handlers junk payload/length.
- Fixed in user_response.c (backup .pre-fix55). hubp61: PipeRole ×2, heartbeat and CreatePage now match hubpstk byte for byte. 0x09 is answered but missing fields 2/3/4/7/8/18. No image reply.

## Fix 56 — settings manager pointer table (sim62)
- Stock RAM 0x200036fc is a .data table of 8 pointers to the KVDB default records. Evidence: stk12 under Renode reads 0 at t=0, and at t=0.05 s 2000380c 200037e0 200037c8 20003818 200037fc 20003824 20003808 200037bc. Ours was zero, so SVC_Settings_Init copied from address 0 and the live settings record was all zeros (DUMP cfg in dp61 vs dpstk).
- Initialised in settings_manager_storage.c (backup .pre-fix56). hubp62: the 0x09 reply is now byte-identical to stock.
- Naming note (not renamed): `audio_settings_als_previous` (+24) actually points to the terminal-mode record, and `_terminal_previous` (+28) to the ALS-scale record. The copy sizes (4 and 12) match the records, so the data is correct.

## Open — image reply (sim62)
- Right arm: after the CreatePage parser calls audio_uart_master_display_start (stock does too), the sync send handler (process_event2) never runs again. Later frames, including the image, are queued OK (putr=0) but never sent to the peer, so the image parser is never reached. In stock, event 2 keeps running.
- Suspect, not yet confirmed: process_event2 hangs, either in the default case (masks interrupts and spins on an unknown node type) or in TF multipart begin/ClaimTx.
- h5p62 (right arm, after the CreatePage parser): master_request_core, then ev2 runs a complete multipart send (begin, ClaimTx, close) and returns normally. So it is **not** the default-case spin or a ClaimTx hang. ev2 is never entered again, so event 2 is no longer serviced although later puts succeed.
- End-of-run PC: right 0x5deb3e (lv_event_send), left 0x5debce (event_is_marked_deleting). Both arms are busy in LVGL, not hung.
- h6p62 audio_mask_save callers after the parser: xPortStimerTickHandler (6461) and vPortEnterCritical (4630), i.e. normal RTOS activity. Not conclusive.
- Next: check whether the uart thread (uart_thread_handler) is blocked on its event-flags wait or starved by a busy display/LVGL thread after display start. Compare thread states and event flags (g2_uart_thread_event) with stock right after dstart. Hypothesis, unverified.

### Image reply — h9/h10 (sim62)
- h9p62: right arm `send_display` (display_slave_send.c) takes the mutex, writes the ring, releases it, then `osMessageQueuePut(0x2000b53c)` never returns, even with its 1000 ms timeout.
- The handle `g2_display_queue` == `&g2_display_queue_control`. With static CMSIS allocation (service_prepare0.c, cb_mem=control, 0x50) the handle *is* the control block, so this is **valid, not the bug**. The earlier "bad handle" hypothesis is withdrawn.
- The consumer is `display_thread.c:295` `audio_uart_queue_receive(g2_display_queue,…)`.
- h10p62 (after the parser): there is 1 `put` and continuous `lv_display_send_event`/`event_send_core` traffic (~2000 hits), i.e. the LVGL refresh is running.
- **Next:** hook `display_thread.c:295` receive entry and return on both arms, to see whether our display thread ever gets back to its queue receive after CreatePage. GUESS: it is busy or blocked in a render path, and the put never returns because the tick or scheduler doesn't reach the UART thread. Unverified.
- Note: the h10 hook `dq=0x4437e0` was a stock address and resolves to `audio_even_ai_rx_config` in ours, so it is invalid. Use the ELF symbol next run.

### Image reply — h11–h23 (sim62, hooks resolved from sim62 ELF)
- h11: ticks are normal (`xTaskIncrementTick` ~1000/s after the parser), so the tick/timeout path is not starved by ticks. Display thread `osMessageQueueGet` is called once (h14), then the thread never loops again.
- So the "blocked put" is a symptom: the display thread (prio 0x2c, higher than the UART thread) is busy inside `handle_start` and never returns to its queue. The UART thread does not get CPU back (scheduler/priority starvation, not a bad handle).
- Chain of non-returning calls (each found by hooking every call's return address):
  `handle_start` → `audio_uart_display_current_set` (0x440754, stock 0x442456 register_all_foreground_ui_pages), 3rd registry callback (r6=0x56fab9) = `audio_uart_registry_callback_4e1dd4` (message_notify_page.c, INIT) → `message_notify_page_init_55225c` (0x58cb54) → item loop `msg_notif_create_msg_item_551814` (0x58c404) → `msg_notif_create_content_obj_5514f0` (0x58c198).
- The first two callbacks (0x56fd65 `_4e2c40`, 0x5590e1 `_46327e`) return normally.
- hubsim.py: added a `name~N=addr` hook form that logs register rN (backup `bak/hubsim.py.pre-regN`).
- h24 (running): return hooks inside `create_content_obj`.
- h24: inside `msg_notif_create_content_obj_5514f0` the last call that returns is `lv_image_set_src(content->separator, g2_msg_notif_separator_icon_76e248)` (0x58c2b0; the descriptor at 0x748b98 is valid: 24×24, data 0x74f1a8). The next call, `lv_obj_align_to(separator, base, 20, 0, r8)` (blx r5=0x5d4629 at 0x58c2c0), **never returns** on the right arm. GUESS: an LVGL layout/refresh loop that never converges (it matches the endless `lv_display_send_event`/`event_send_core` traffic in h10). Unverified; h25 is counting `lv_obj_update_layout`/`layout_update_core`/`refr_size`/`refr_pos`/`mark_layout_as_dirty`.
- h25: `lv_obj_align_to` → `lv_obj_update_layout(r0=0x201bc268)` is entered once; `layout_update_core` is never reached. The spin is in `lv_obj_get_screen` (0x5d9994), whose loop is `while ((p = lv_obj_get_parent(o)) != NULL) o = p;` and exits only on a NULL parent. So the parent chain from the separator never reaches NULL (a cycle, or garbage pointers).
- h26 (args at the `blx r5` site 0x58c2c0, right arm): obj=`content->separator`=0x201bc268, base=`content->title`=**NULL**. Dump of 0x201bc268: `6cc31b20 00000001 40831b20 04ec1b20 …`. word0 (class_p) is a RAM pointer (0x201bc36c), not a ROM lv_obj_class, so **the object is not a valid lv_obj** (heap garbage / overlapping allocation).
- **Finding:** when the message-notify page is built at display start, `content->title` is NULL and `content->separator` points at a corrupt object, so LVGL loops forever in `lv_obj_get_screen`. The display thread (prio 0x2c) spins, the UART thread is starved, and `send_display`'s `osMessageQueuePut` "never returns" — so there is no image reply.
- GUESS (next to verify): LVGL heap exhausted or overlapping (label/image create returning NULL or reused memory). Check the return values of `lv_label_create`/`audio_uart_page_498668` here, the LVGL pool base/size against stock, and compare `title`/`separator` on stock's 0x5514f0.

### Fix 57 — image reply root cause: lv_image_set_src header buffer overflow (sim62 h27/h28)
- h27: the content creates are fine (title=0x201bea64, separator=0x201beb70); the content struct layout matches stock 0x5514f0 (memset 0x1c; stores at +0,+4,+0x14,+8,+0xc,+0x10,+0x18). The LVGL pool (0x201b8340, 0x2d000, its own array) has no linker overlap.
- h28: in `create_content_obj`, r4 (content=0x2005de38) is **0x18** after `lv_image_set_src` (`audio_uart_page_498680`, 0x48e228) returns. That function's prologue/epilogue are correct, so its saved-r4 stack slot is overwritten.
- Cause: `display_image_set_src_498680.c` had `uint32_t header[2]` at sp+40, 8 bytes below the saved regs, but `audio_uart_lv_image_header_488f6a` (lv_image_decoder_get_info) writes a 12-byte LVGL 9 `lv_image_header_t`. The separator's header word 2 (stride=0x18) landed on saved r4. The caller then used r4=0x18 as `content`, read title=NULL and separator=garbage 0x201bc268, and `lv_obj_get_screen` looped forever. The display thread (prio 0x2c) starved the UART thread, so `send_display`'s queue put "never returned".
- Evidence: stock 0x498680 passes `add r1, sp, #12` with the next local at sp+32 (≥12 bytes); the other callers (onboarding.c, dashboard.c, draw_task_render) already use 12-byte headers (`_Static_assert ... == 12`).
- Fix: `uint32_t header[3]` (backup `bak/display_image_set_src_498680.c.pre-fix57.orig`). sim63 is building.
- **Verified (sim63, paired hubp63 vs hubpstk):** build 2870/2870, 0 undefined. Ours now sends 9 of stock's 10 frames in the same order with identical payloads: PipeRole cmd4/5 ×4, 0x09 cmd2 (field 2=100), cmd14, 0xE0 result, and the **image reply cmd4 (container "img", id 2, 189 B, status 4)**. Both arms end at PC 0x4a720c (no spin).
  - Only diffs: the magic byte of the two flags=0x1 heartbeat frames (ours 67/175 vs stock 41/149; a runtime counter, GUESS timing-dependent), and stock's trailing unsolicited 0x09 battery frame (field 2=70), which ours still does not send. That is the next item.

## Stack-buffer sweep (after Fix 57)

**Static (`.waves/sim-fix/stackgap.py`).** For every `add rN, sp, #off` passed as r0-r3 to a bl, gap = next buffer base (`add rX, sp`) or frame top minus off; flag when ours < min stock gap for the same callee.
- Fixed two script bugs: stock raw-bin `bl 0x...` targets were skipped (no `<sym>`), and scalar `[sp,#k]` slots inside a buffer made gaps falsely small.
- Validation: sim62 flags `audio_uart_page_498680` callee 0x488f6a buf sp+40, ours 8 < stock 12 (the Fix 57 bug); sim63 no longer flags it.
- sim63: 105 flags, list in `.waves/sim-fix/stackgap_sim63.txt`. Not yet triaged. GUESS: many are false positives. Negative gaps are outgoing-arg/frame-top artefacts (cli_cmd_* -> 0x5848fc); 4-vs-8 nema_vg rows are probably clang packing scalars differently.
- Priority triage (large stock reserve): efs_service_init_458c48 (1 vs 304), registry_callback_58607a (44 vs 648), attsProcMtuReq_56c6fc (1 vs 24), audio_terminal_ui_tick_5e8008 (7 vs 36), audio_ble_radio_exchange_begin_52e0d2 (16 vs 48), teleprompt_action_app_start_58ca2a (8 vs 52), quicklist_format_timestamp_4f5366 (12 vs 40), display_driver_uled_command_5926ee (28 vs 56).

**Dynamic (SSP).** Env var `G2_SIM_EXTRA_CFLAGS` (apollo-main only, `tools/build/sources.py`), plus `EXTRA_OBJ` in linksim.sh and `.waves/sim-fix/ssp/ssp_stub.o` (spinning `__stack_chk_fail`, hook with `@`).
- sim64 `-fstack-protector-all`: link fails; `.text` overflows MRAM by 340859 B.
- sim65 `-fstack-protector-strong`: building.

### SSP run (sim65) and static triage
- sim65 `-fstack-protector-strong`: links, 0 undefined (`nm -u`); `__stack_chk_fail` = 0x62cae0 (sim65 ELF). Boots to display.
- Paired hubp65 with `sspf@=0x62cae0`: hook armed on left and right (renode.log AddHook), **0 hits**; both cores idle at 0x4aa718. Frames identical to hubp63 except the heartbeat magic counters (0x43/0xaf vs 0x3e/0xaa; GUESS timing, as before). No canary fault on the paired boot/hub path. Coverage limit: only code exercised by this run.
- stackgap.py frame now from prologue only (plus dummy r0-r3 push slots). Still flags 498680 on sim62. sim63: 123 rows (`.waves/sim-fix/stackgap_sim63.txt`). Hand-checked, all false positives:
  - efs_service_init_458c48: stock uses 1 byte at `[sp]` of `push {r7,lr}` (0x458c4c); ours 1-byte local. Stock 304 is a slice overrun into 0x458c5e.
  - quicklist_format_timestamp_4f5366: ours `when` at sp+116 in a 156-B frame = 40 B = 40-B record written by 0x449fda (put32 up to +32). The "12" is an interior `add sp,#128` base.
  - teleprompt_action_app_start_58ca2a: 0x48eb32 takes (ptr,len<=8) read-only; stock passes len 2 (0x58caa6). Ours has 8 B.
- Conclusion: the static metric is low-precision; SSP is the trusted detector. No new stack fixes this round.

## Unsolicited service-0x09 frame (stock field 2 = 70)
- The frame is `setting_notify_common` 0x49bbfc -> Thread_MsgPbNotifyByBle type 1 / cmd 9 (device status). Correction: field 2 = 70 is GUESS an ALS brightness level, not battery (the solicited reply has 100).
- Hooks h5pstk / hubp63b on notify_device_status 0x49be04 / ours 0x44f708 (LR):
  - stock: 46b44b x2 per core, 46bb6f x1 (right) and **4ae809 x1 per core**; right-core notify_common x4.
  - ours: 483d95 x2 per core, 44fec3 x1 (right); notify_common x3.
  - The only missing call is from 0x4ae804 = ALSSyncHandler 0x4ae73c (ours `audio_uart_registry_callback_4ae73c`, `als_sync_registry_4ae73c.c`; registry event 0x10e). The source matches stock 0x4ae73c..0x4ae80a instruction for instruction.
- Hooks h6pstk / hubp63c at handler entry: stock 16 calls per core (LR 0x44255d, len 2); **ours 0** (AddHook 0x484f18 confirmed armed). So ours never publishes ALS sync 0x10e: `als_function_01` 0x4ad9b8 <- `als_function_23` 0x4adf04 <- ALS timer handlers 0x4ae2b6 / 0x4ae3c8.
- Next: hooks on ALS open/close/start/adjust/poll/timer (h7pstk / hubp63d).

## ramdup triage
- `.waves/sim-fix/ramsplit.py` resolves each RAM-tagged declaration per candidate address in the sim63 ELF: 90 ok (one address), 5 unresolved (no declaration parsed), 2 SPLIT.
  - 0x20000040: parse artefact (`exists` is code).
  - 0x20075010: real two-object split, but benign. `g2_stock_ram_20075010[16]` (stock_ram_cells.c:1980) is only used at +3..+6 (codec request/lifecycle, HCI radio); +0/+1/+2 are each used only through `audio_box_reconnect_suppressed_20075010`, `audio_box_reconnect_pending_20075011` and `audio_uart_case_status_disabled` (.g2_ram_20075012). Disjoint bytes, no fix.
- 0x2000b534: `audio_uart_input_queue` and `g2_display_queue` resolve to the same ELF address (alias of one object, `g2_display_queue_control` at +8). Benign.

### ALS trace and Fix 58
- h7pstk vs hubp63d (ALS hooks): stock right core calls DRV_ALSOpen 0x4ae10a once (LR 0x4a7137, in hub func-open handler 0x4ae... range 0x4a6ee8), then timer 0x4ae6d0 x20, adjust 0x4ae3c8 x16, als_function_23 x16. **Ours: 0 hits on all ALS hooks** (AddHook armed).
- Opening is gated by SVC_Settings_AutoBrightnessOpen 0x46c01c: `ldr r0,=0x20072da8; ldrb r0,[r0,#2]` (0x46c02a..0x46c02e). Configure 0x46c158 writes `strb [0x20072da8,#2]` (0x46c164) and `str [#4]` (0x46c17e).
- Ours defined `audio_uart_auto_brightness_enabled_cell` / `_profile_cell` as standalone .bss (0x20080000/4), not `audio_settings_config_live`+2/+4 (ours 0x20003a88). The cell was never set from config, so we got "auto brightness disabled" and ALS never opened. (`setting_manual_brightness_46c1c8.c` already reads `audio_settings_config_live[2]` correctly.)
- **Fix 58:** `display_auto_brightness.c` / `_configure.c` map both names to `audio_settings_config_live+2u/+4u` with citations; definitions removed from `_state.c`. Backups `bak/*.pre-fix58.orig`.
- sim66: links, 0 undefined (`nm -u`), the cells are gone from nm. Paired hubp66 running.
- Lesson: ramsplit.py misses single-declaration splits where a cell has its own object but stock accesses it as base+offset. Follow-up sweep: compare RAM-tagged standalone objects against stock literal-pool base+imm accesses.
- **sim66 verified (hubp66).** Hooks now match stock h6pstk/h7pstk:
  - ALS open x1 (right).
  - ALSSyncHandler x16 per core.
  - notify_device_status from the handler (LR 0x484fab) x1 per core.
- 10/10 frames identical in payload to stock h4pstk, including the unsolicited 0x09 frame `0802100422231046...` (magic 4, field 2 = 70). Only differences: the two heartbeat magic counters (0x43/0xaf vs stock 0x29/0x95; GUESS timing, unchanged since sim63).

## Fix 59 — display-manager queue split (basesplit hit a), sim67

- Stock: every display-manager reader loads the queue as `[0x20000658,#12]` (`ldr r0,[r0,#12]` at 0x473b74, 0x473bea, 0x473c7a, 0x473e4e, 0x473ec0, 0x473f32, 0x473fa4, 0x474018, 0x4740a8; `[r4,#12]` at 0x4741fc, 0x4743ce).
- Ours: the queue is created into `audio_display_driver_manager.queue` (+0xc, `display_driver_callbacks.c:63`). But the init/deinit-force, flush-view and state-table code read a separate `audio_uart_display_manager_queue_cell` (`.g2_ram_20000664`, linked at 0x20006230) that nothing writes, so those readers always got a 0 queue.
- Fix: in those 4 users, the cell is now a macro over `audio_display_driver_manager + 0xc` (via an `__asm__` name reference), with a citation. The definition is replaced by a comment plus a typedef. Backups: `bak/*.pre-fix59.orig`.
- sim67: links with 0 undefined and the cell symbol is gone. The paired run `h67p` decodes the same as hubp66 (176 lines); the only diff is syncId 190→195 (timing, guess). The fixed path hasn't been confirmed to run in this scenario (no hook yet).

## basesplit hit b — 0x20073298 (open)

- Stock `am_hal_spotmgr_post_lptohp_handle` 0x4803dc calls the callback at `[0x20073270,#40]`. Ours has three overlapping views of stock 0x20073270:
  - `g2_spotmgr_state` (0x3c)
  - `g2_stock_ram_20073270` (0x28, used by `power.c` +4)
  - `g2_stock_ram_20073298` (0x90, used by `pin_mux_attributed_data.c` and `transition-snapshot/producers.c`)
- Still to do: find which view the stock registration writes, then unify them.

## Fix 59 reachability (h67q / hstkq)

- Hooked ours flush/init-force/deinit-force (0x48e060/0x444e14/0x44121c) and stock 0x474066/0x474100/0x47432c. There were 0 hits on both sides, so this scenario never runs the fixed path. The fix rests on the static evidence only. `osMessageQueuePut` hits in ours were all on non-zero queues.

## basesplit hit b — 0x20073298: benign (closed)

- In stock, the only literal for this region is 0x20073270, at pool 0x4806fc. It's used only by the spotmgr dispatchers, and its table is filled by `am_hal_spotmgr_init` (ours: `g2_spotmgr_state`, matching). No stock literal 0x20073298 exists.
- The `producers.c` readers of `g2_stock_ram_20073298` come from an offline-reconstruction literal: `pcm22_registered_timer_service` / `pcm22_timer15_vector_handler` / `pcm22_registered_post_low_to_high` (0x495cf0/0x495d04/0x495d18 in sim67). They have no `bl` callers and no address words in the image, so they're dead code. No edit.

## Canary sim68 + wider EvenHub coverage (w68 vs wstk)

- sim68 = sim67 + `-fstack-protector-strong` + SSP stub (`__stack_chk_fail` 0x62cad0). It links with 0 undefined.
- `adapter.ts` has a new opt-in `WIDE=1` plan (backup `bak/adapter.ts.pre-wide`; the default plan is unchanged). After the base steps it sends Rebuild(list+text), TextUpgrade, EvenHub HeartBeat, ImuControl on/off, and Rebuild with a menu.
- Results: the canary had 0 hits. All 14 per-step notification counts match stock; decoded messages match, apart from the devcfg heartbeat magic counters.
  - Rebuild, TextUpgrade, HubHeartbeat and Rebuild(menu) produce no notification on either side.
  - ImuOn gives result code 1 and ImuOff code 0 on both sides.
  - Firmware reports 2.2.6.10, so menus (fw ≥ 2.3) aren't expected to work.
- Only divergence: stock emits the unsolicited 0x09 ALS frame (field 2 = 70) during the `long` touch window; ours emits it later, in the closing 5 s run. Same frame, same total of 12. Guess: timing.
- Gaps:
  - Touch frames set attention but produce no EvenHub list/text event on either side, so gesture-to-UI isn't exercised yet.
  - `evenhub/src/setting.ts` has only a status request, so there are no settings-write encoders.
  - No hook yet proves Rebuild/TextUpgrade are handled rather than dropped (both sides are silent).

## EvenHub handler hooks (x68 vs xstk, WIDE plan)

- Hooked page-create, rebuild, list-rebuild, text-config, the inject adapters, the send-*-event functions, the page-event handler and reflash. Pairs, ours ↔ stock:
  - 0x55a7b4↔0x494bec, 0x55b0ac↔0x4955b4, 0x564200↔0x493ab6, 0x55b030↔0x495f1a
  - 0x559fd8↔0x494610, 0x55a30c↔0x495f9a, 0x55a4b8↔0x4961e4
  - 0x571944↔0x4da16a, 0x571b18↔0x4da382, 0x5716b8↔0x4d9d9a, 0x579230↔0x4e0d3a, 0x55b8d8↔0x496544
- Counts are identical on both sides:
  - pcreate 1/arm, textcfg 1/arm, pevt 92/arm, ievt 1 (right arm only)
  - rebuild, list-rebuild, the inject adapters and reflash: 0
- This matches evenhub/docs/REFERENCES-NOTES.md §1: rebuild and text-update success replies come from the UI-thread display-refresh path, which this scenario never drives on either image. So "no reply" there is parity, not a bug.
- Touch: the inject adapters are never hit, because rebuild never binds the list. The create page's capture container is a text container, and on text a click is a sysEvent. Next: per notes §2, inject through the bound adapter 0x495f9a on the right arm after a working create with a list capture container.

## Settings writes (s68 vs sstk)

- `adapter.ts` WIDE plan: writes now use `encodeSettingWrite` from evenhub, imported without editing it (backup `bak/adapter.ts.pre-setw`). Layout cross-checked against the stock nanopb descriptors: root 0x77772c, DeviceReceiveInfo 0x777804, scalar members {1:uint32} e.g. 0x77775c.
- Steps: screenHeight 7 (t2), screenDepth 2 (t3), silentMode on (t6), headUp on + 30° (t4), then a status request.
- Hooks (ours↔stock): process 0x44d3c4↔0x466976, dispatch 0x44d69c↔0x466abc, t2/t3/t4/t6, respond 0x44eda4↔0x49b900.
  - Identical on both arms: proc 6, disp 4, resp 4, t2=7, t3=2, t6=1, t4 1.
- Config RAM dump (ours 0x20003a88 / stock 0x20072da8, 0x20 bytes) is byte-identical: `0446010000000000070201001e00...`.
- The status reply after the writes reports field3=7, field4=2 on both sides.
- Only diff: devcfg heartbeat magic counters (known timing issue, guess). Canary (sim68 SSP) had 0 hits.

## List-capture page + extra settings types (l68 vs lstk)

- `adapter.ts`: added `LISTPAGE=1`, which makes CreatePage carry a capture list (ID 5, 'cl', 3 items) with the title text not capturing. Added `SETX=1` writes for inner tags 5/7/8/12 as `{1:v}`; the meanings are a GUESS, though the scalar layout is from descriptors 0x7777a4/0x7777d4/0x7777ec/0x7778f4. Backup: `bak/adapter.ts.pre-listpage`.
- Hooks ours↔stock:
  - bind 0x564828↔0x4942a4
  - list/text adapters 0x55a30c↔0x495f9a, 0x55a4b8↔0x4961e4
  - common list inject 0x5760f8↔0x4de354, list/text callbacks 0x55a1a4↔0x4949c0, 0x55a258↔0x494a78
  - send input/system/container events
  - wear 0x48c95c↔0x49eb1e, t8 0x44dbc4↔0x4671a2, t12 0x44d9a0↔0x467c34, respond
- Identical on both sides:
  - bind 1/arm (list bound)
  - wear=1, t8=0, t12 1/arm
  - respond 8/arm
  - ievt 1 (right arm only); the caller is the EvenHub data parser (ours 0x572c08 in `evenhub_data_parser_4da834`; stock 0x4db98a), not touch
  - adapters, inject, callbacks and sys/container events: 0
- Decoded notifications match (23); only the heartbeat magic differs.
- Touch: the 5 temple frames are published and consumed (5/5) but never reach the bound adapter on either side. The emulator's temple stimuli (`src/g2emu/foreground_gestures.py`) cover only long press, release and tap-long. The report's gesture word (offset 10, `G2CY8C4046FNI.cs`) is 0 in them, and the `probe-r1-connected.py` swipe/tap gestures are for the R1 ring, not the temple. Classification happens in `gesture_touch_event_process_502ef4`, which ours links from stock unchanged. Next: hook it on both sides and find the report bytes for click and swipe up/down (unknown so far).
- The rebuild/text-update success path (display refresh → UI thread) hasn't been driven yet; no reply on either side, as before.

## Temple touch classification + display-refresh path (g68/gstk, r68/rstk)

- Report byte 1 is a SLIDER_EVENT bit set, decoded from stock `0x502dc2` with name literals at 0x503250..0x50326c:
  - 0x01 PRESS, 0x02 RELEASE, 0x04 SINGLE, 0x08 DOUBLE, 0x10 LONG, 0x20 SLIDE_L, 0x40 SLIDE_R, 0x80 ERROR (resets the controller via 0x55b64a/0x55b6dc)
  - The bit order follows the literal order (`lsls #31/#30/...` tests); it's a GUESS for the upper bits.
- So the old hubsim "tap?" frame (0x08) is a DOUBLE.
- hubsim now takes `TOUCHX="name=hex ..."` extra frames (backup `bak/hubsim.py.pre-touchx`). Added slideR 0x40, slideL 0x20 and single 0x04, with byte2=1.
- gproc (ours 0x5896a4 / stock 0x502ef4) runs once per frame on the right arm, 10/10 on both sides.
- Forwarding via `ring_touch_event` (ours 0x48c328 / stock 0x4c5916): identical codes on both sides (0, 1, 3×2, 4, 5, 0xe×2).
- Still 0 hits on the bound list adapter / list callback, on both sides.
- `master_display_refresh` (ours 0x446c18 / stock 0x464bb2) is called 5× with app 0xe0 on the right arm on both sides. `evenhub_ui_page_rebuild` (0x55b0ac / 0x4955b4) is still 0 on both.
  - So the parser hands rebuild/text/etc. to the display-refresh pipeline, but the UI-thread consumer never processes it in either image. Rebuild and text-update replies and touch→list are blocked by the same missing UI-side step; it's not an ours-vs-stock divergence.
- `quicklist_refresh_enabled` (ours 0x44a530 / stock 0x4434d0): 16 right + 2 left calls on both sides, through different call sites (ours inlines/merges parser branches; caller sets 0x5595ad/0x572989/0x572f43 vs 0x46804f/0x4dac8d.../0x4db979). The counts match; I didn't inspect it further.
- Next: follow `master_display_refresh` → its queue/sync target → the UI thread receive loop, and find why neither image's UI thread runs the EvenHub handler. Candidates: the display-manager queue (Fix 59 area), the foreground app id, or a sync message from the left arm the emulator doesn't deliver.

## Display-refresh → UI thread trace (runs u68 / ustk, WIDE=1 PAIRED=1)

Path: `master_display_refresh` (ours 0x446c18 / stock 0x464bb2) → `audio_uart_master_request_core_464772`
(ours 0x4467d4). Role 1 (master) enqueues the packet onto `audio_uart_master_schedule_queue` (ours 0x20081e48);
role 2 (slave) enqueues it onto `g2_uart_send_queue` (ours 0x2000750c). The UI-side consumer is the EvenHub
registry callback `audio_uart_registry_callback_4e1490` (ours 0x57964c / stock 0x4e1490): event 2 = STARTUP
(page create), 3 = DISPLAY_REFLASH (→ `evenhub_ui_reflash_event_handler_496544`), 4 = AUTO_REFLASH.

Hook counts (identical shape on both images):

| hook | ours u68 | stock ustk |
|---|---|---|
| uicb r0 (event) | left 1×2, right 1×2 | left 1×2, right 1×2 |
| page_create 494bec | 1 per arm | 1 per arm |
| master_display_refresh (right) | 5 | 5 |
| reflash handler 496544 | 0 | 0 |
| loading-page UI handler 492fdc | 0 | 0 |

Finding: STARTUP reaches the UI callback and the page is created on both arms, but none of the 5 refreshes reaches
the UI callback as event 3, on **either** image. The drop happens between the master schedule queue and the UI
dispatch (sync_schedule_manager). This is not an ours-vs-stock difference: it is a sim/harness limitation, probably
the schedule thread waiting for a peer UART ack that the paired sim does not model (guess, not yet verified).
AUTO_REFLASH (4) never arrives either, which suggests the periodic UI tick is not running (guess).

### Correction: refresh drop located (runs s68, t68/tstk, d68/dstk, f68/fstk, n68/nstk)

The "peer UART ack" guess above is **wrong**. Each hop, ours / stock:

1. Scheduler (ours 0x55c768): all 5 CMD_REFRESH (cmd 3) are forwarded (`rfwd`/`rdone` 5×, s68). The stock branch
   addresses I guessed (0x45ccd2/0x45cd3a) did not hit, so this hop is unverified for stock.
2. UART link: `audio_uart_slave_display_refresh(0xe0)` runs 5× on **both** arms in both images, with no send
   timeouts (t68/tstk). The link works.
3. `send_display` puts each refresh on `g2_display_queue`. The display thread handles type 3 (refresh) and its
   16-tick timeout (AUTO_REFLASH 4) only when `display_state==1`.
4. `handle_start` (in the display thread) sets state 1 and sends STARTUP (seen), then calls `current_set`,
   `channel_set`, `layer_prepare`, `audio_uart_display_process`. `sync_info` is never reached, on both images
   (d68/dstk). So the display thread blocks inside `audio_uart_display_process` = `lv_timer_handler`
   (ours 0x5f2f98 / stock 0x464344).
5. Inside it, `draw_buf_flush` (ours 0x5eaadc) is entered once and `call_flush_cb` never runs (f68). The display
   thread spins in `render_wait_484622` (`lv_thread_sync_wait`) waiting for the draw unit.
6. The Ambiq render thread (ours 0x4a9ce0 / stock 0x4c7700) runs one draw, then never signals completion.
   Stock is seen entering `nema_cl_wait` / `nema_wait_irq` (0x514d00 / 0x51400a); `nema_gpu_irq_service` never
   runs (n68/nstk).
7. Emulator log, both images, both arms: `right|left/gpu: Unqualified GPU ring-stop control flags; command
   processor stopped without completing pending work`. In `renode/peripherals/G2NemaGpu.cs`, a write to RING_STOP
   (0xEC) with a mode other than 4 or 6 faults the model, so no fence IRQ is raised.

**Root cause: an emulator limitation, the same for ours and stock.** The NemaGPU model rejects the firmware's
RING_STOP mode, so the GPU IRQ never fires. That blocks LVGL rendering, so the display thread never reaches the
running state, so refresh and AUTO_REFLASH events never reach any app UI. Not a firmware divergence.
Emulator diagnostic edit (message only; backup `bak/G2NemaGpu.cs.pre-ringstop`): the warning now includes the
written value.

RING_STOP values rejected by the model (run g68v, ours, both arms): 0x200EBF9E (2×), 0x200EC10C, 0x200EC12C.
Low nibble 0xE / 0xC means bit 3 is set, which the model doesn't accept (only 4 and 6).
**Guess:** these look like ring write-pointer addresses in SRAM (0x200E….), not "base|flags" words. 0x…F9E is
not even 4-byte aligned, so the model's `value & 0xF` = mode decode is probably wrong for these writes. Not yet
checked against the NemaGFX `nema_cl_submit` / ring-stop source. Sim-side fix pending a decision; no model
semantics changed yet.

### Sim-side fix: G2NemaGpu RING_STOP decode (emulator only, local, uncommitted)

Evidence:
- sim68 disassembly: `nema_rb_init` 0x4ac7dc writes RING_STOP = `base_phys|6`, then CMDADDR = base, CMDSIZE.
- Submits (`register_emit` 0x4abc70, `nema_submit` 0x4ac35c, `packet_emit`) write `(base + offset*4)|4`.
- Diagnostic run g68w logged ring base 0x200EBF98 (8-aligned, address bit 3 set):
  init 0x200EBF9E = base|6; submits 0x200EC10C = 0x200EC108|4 and 0x200EC12C = 0x200EC128|4.

The model decoded `value & 0xF` as the mode, so it misread address bit 3 as a flag and faulted.

Fix: in `renode/peripherals/G2NemaGpu.cs`, mode = `value & 0x7` and stopAddress = `value & ~0x7`. Ring entries
are 8-byte pairs, so bits [2:0] are free. The fail message now includes the value; the temporary RSDBG log was
removed. Backup: `.waves/sim-fix/bak/G2NemaGpu.cs.pre-ringstop`.

### Emulator upstream/fork survey (2026-10-27) and local import

Remotes added locally, fetch only: `jim` (jimrandomh fork), `eropple`. No PRs (open or closed) on
PaulMcMillan/g2-firmware-emulator. Both forks' master == upstream master; neither fork has other branches.
- `origin/jim-emulator-dev` (James Babcock, 2 commits, 2026-10-04): "Implement enough of the GPU to show the stock
  dashboard" + "Performance optimizations". Adds `TryGeneralDraw` / rasterizer, texture binding,
  `SkipUnsupportedDraws`, and MSPI / SystemTimer / Watchdog tweaks across 316 files. It still has the
  `value & 0xF` RING_STOP decode bug.
- `foreground-*-preparation`, `ota-clock-reuse-preparation`, `runtime-census-preparation`: docs, scripts, g2emu
  and tests only.
- `ota-*` (5 branches, 118 behind): EM9305 / IOM SPI timing and OTA trace peripherals. No GPU changes.

Imported: only `renode/peripherals/G2NemaGpu.cs` from `jim-emulator-dev`, as a working-tree copy via `git show`
(no checkout or merge), with the 3-bit RING_STOP fix applied on top. Backups: `bak/G2NemaGpu.cs.pre-ringstop`
(upstream) and `bak/G2NemaGpu.cs.ringfix-only`. The rest of jim's branch is not imported: that would need a
merge or checkout in the emulator repo.
hubsim gains opt-in `GPUX=1` (ExperimentalFragmentMode) and `GPUSKIP=1` (SkipUnsupportedDraws).
Backup: `bak/hubsim.py.pre-gpux`.

### UI refresh unblocked: paired runs with the fixed GPU model (WIDE=1 LISTPAGE=1 PAIRED=1)

| run | GPU log | GPU ISR | UI events (both arms) | refresh handler | rebuild | list adapter | notifs (80/09/e0/0d) |
|---|---|---|---|---|---|---|---|
| x68 / xstk (ring fix only) | unimplemented draw 0x2 shader 0x181F8000 | 1/arm | 2×1 | 0 | 0 | 0 | 6/1/2/0, both |
| j68 / jstk (+ jim GPU) | same draw failure | 1/arm | 2×1 | 0 | 0 | 0 | same |
| k68 (+ GPUSKIP=1) | none | L907 R743 | 2:2 3:10 4:652 5:2 | 5/arm | 2/arm | 0 | 6/11/9/4 |
| kstk (+ GPUSKIP=1) | none | 421/arm | 2:2 3:10 4:648 5:2 | 5/arm | 2/arm | 0 | 6/11/9/4 |

- With GPUSKIP, refresh and AUTO_REFLASH reach the EvenHub UI on both images, and the rebuild/text-update replies
  now go out: 9 EvenHub (0xe0) frames, up from 2.
- k68 vs kstk notifications: all 30 frames match once byte 2 (sequence) and the CRC are masked, except idx 1 and 4,
  the known heartbeat magic counters. **Ours matches stock.**
- GPU ISR count differs (ours L907 R743 vs stock 421/arm). Probably rendering/timing differences under skipped
  draws; not investigated (guess).
- Touch→list is still blocked: the list adapter (ours 0x55a30c / stock 0x495f9a) has 0 hits on both images. This
  is the next item.
- Caveat: GPUSKIP skips the unimplemented draw (0x2, shader 0x181F8000), so framebuffer contents are not
  faithful. Event and protocol paths only.

### Touch → list, step 1 (t1_68 / t1stk; GPUSKIP, LISTPAGE, extra single-tap frames 0x04, a guess)
- `ring_touch_event` r1 codes on the right arm: 0×2, 1×1, 3×2, 0xe×4. **Identical on both images.**
- Ours scheduler CMD_INPUT forward: 11× (`inp`/`indone`).
- UI events per arm: 2×1, 3×5, 5×1 (EXIT) on both images. A gesture probably exits the app (double-tap →
  dashboard; guess).
- LVGL page events: same codes; counts 16 (ours) vs 24 (stock) for 0x1a/0x1f/0x20/0x21 (timing, guess).
- List adapter: 0 hits on both images. Next: find which touch code maps to select / CLICK, and send it before any
  exit gesture.

### Full import of jim-emulator-dev into the emulator working tree (user-approved; no commit)

The jimrandomh fork has nothing beyond upstream master. All of jim's work is `origin/jim-emulator-dev`, 2 commits
on merge-base f30527c (== local master):
- **29b7ecb "Implement enough of the GPU to show the stock dashboard; clean up some hash-verification issues"**
  - G2NemaGpu +544: opt-in `GeneralDrawPolicy` fallback rasterizer with texture binding, `QuadRasterPolicy`
    (edge-grid4), `FractionalBlendPolicy` (floor255), `SkipUnsupportedDraws` with signatures and snapshots.
  - New live UI `g2ui`: live.py / live_ui.py / live_ui.html serve both panels at 127.0.0.1:8765 and turn touchpad
    gestures into CY8 reports.
  - New `inputs.py` provenance module. About 250 g2emu, scripts and tests files replace frozen SHA-256 constants
    with live `inputs.digest()`.
  - `scripts/gpu-frontier.py`; docs nema-general-pipeline / live-ui / provenance; tests.
- **9a19857 "Performance optimizations"**
  - MSPI / SystemTimer / Watchdog models: idle acceleration, STIMER poll-spin skip, watchdog restart coalescing.
  - G2NemaGpu perf tweaks.
  - renode_console: per-session Renode config with command history kept out of the session. The optional Renode
    patches `renode-shell-history-optional` and `renode-tlib-darwin-setjmp` are wired into bootstrap-renode.sh.
    The current Renode build is unpatched and falls back to a per-run history path, so no Renode rebuild was done.
  - docs/emulator-performance.md reports a static dashboard at ~12 → ~1.0 wall-s per virtual second.

How applied: backup tarball `bak/emu-pre-jim.tgz` (301 existing files), worktree GPU file reset to upstream content
from `bak/G2NemaGpu.cs.pre-ringstop`, then `git diff f30527c origin/jim-emulator-dev | git apply --3way`. Clean,
316 paths. Side effect: `--3way` also staged them in the index; nothing was committed. The worktree now equals
jim-emulator-dev plus only the 3-bit RING_STOP fix (6+/3-).
hubsim: new opt-in `GPUJIM=1` sets the live-UI GPU options (blend 1, fragments, quad 1, general 1).
Backup: `bak/hubsim.py.pre-gpujim`.

#### Post-import paired verification (t1 touch frames + full hook set, WIDE LISTPAGE PAIRED)
| run | GPU opts | result |
|---|---|---|
| js68 / jsstk | GPUSKIP=1 | Notifs byte-identical to pre-import t1_68 / t1stk (30/30 each). Hooks unchanged: uicb 2:1 3:5 4:326/324 5:1; rfl 5, rbd 2; rte r1 0×2 1×1 3×2 e×4; ours inp 11; pev 16-set (ours) vs 24-set (stock); lst 0 on both. |
| jg68 / jgstk | GPUJIM=1, no skip | No `Unimplemented GPU draw` fault; jim's GeneralDrawPolicy covers draw 0x2 shader 0x181F8000. Hooks and notifs identical to js68 / jsstk. |

- gisr: ours L907 / R743 vs stock 421 per arm in every run (timing, guess).
- Ours vs stock notifs differ only at idx 1 and 4 (heartbeat counters).
- Not rerun: plain no-skip without GPUJIM. Pre-import j68 shows it halts on draw 0x2 by design.

Conclusion: the import is neutral for both images. GPUJIM=1 is now the preferred non-skip mode.
Touch-to-list remains open: the list adapter is never entered, and the gesture sequence reaches exit (uicb 5) on both.

### Touch to list: reached (runs to68/tostk, ns68/nsstk; GPUJIM=1 WIDE LISTPAGE PAIRED)
Why the earlier runs exited:
- The hubsim base touch sequence starts with `tap?` = `0008…`. Report byte 1 is the slider mask (service_gesture_processor.c), and 0x08 is DOUBLE → input 1.
- New `TOUCHONLY=1` drops the base frames. to68/tostk then saw only `rte` 0/e/0/e (TOUCHX SINGLE diffX 1 / 0, RELEASE), but uicb 5 still fired.
- uicb 5 fires at the `Silent(t6=1)` inject: varint 0x5e700006 in the L2CAP frame, before any touch. Enabling silent mode closes the EvenHub page on both images (seen; that this is intended firmware behavior is a guess).
- New adapter.ts `NOSILENT=1` skips that step.

ns68 / nsstk (NOSILENT TOUCHONLY):

| | ours | stock |
|---|---|---|
| uicb 5 (exit) | 0 | 0 |
| list adapter `lst` | 2 / arm | 2 / arm |
| rfl / rbd | 7 / 2 | 7 / 2 |
| uicb 3 | 7 | 7 |
| new page events | 0x4a ×2, 0x0a ×2 | same |
| notifs | 23: e0 10, 80 6, 09 6, 0d 1 | same |

- Masked notifs are identical except idx 1 and 4 (heartbeat counters).
- Last two notifs, one per tap: `aa120f0101e00108026a090a0708031203 6c7374`, i.e. EvenHub field 13 {1:{1:3, 2:"lst"}}: a list event for container 3 "lst".
- GUESS: no selected-item index is present, either because it is 0 and proto3 omits it, or because a field is missing. Not yet checked against the stock encoder.
- pev 16-set (ours) vs 24-set (stock) is unchanged (LVGL style/layout count; benign so far, unverified).

Next: decode the list-event proto against evenhub/ (read-only) and send a SLIDE then a SINGLE to check that the selected index changes.

### List event decode, slide then tap, LVGL page-event diff (runs sh68/shstk, sw68/swstk; GPUJIM NOSILENT TOUCHONLY)
Decode (evenhub/proto/evenhub.proto, read-only): `aa12..0101e001 08 02 6a 09 0a 07 08 03 12 03 "lst"` is DeviceEvent{ list=1: ListEvent{ container_id=3, container_name="lst" } }.
`item_name`, `item_index` and `event_type` are absent from the wire (proto3 omits default 0/""). So: index 0 (hook `lcb`: `common_list_event_callback` arg selected_index = 0), event_type 0 (click, via `evenhub_send_container_event(0,0,NULL,0,idx)` in the page handler). item_name empty: GUESS, since the hook only read the index and the name pointer wasn't read.

Slide then tap (`slideL` = report 0x20, diffX 0x0a, speed 5; release; wait 1 s; `single`; release; wait 1 s), `sw68 / swstk`:
- Slide: rte=5 (DOWNROLL) → page event 0x45 (SCROLL_DOWN) → list adapter → `evenhub_send_input_event` (private event cmd 0x0b, peer-bound; the phone sees nothing, as expected for scroll). Same on both.
- Tap: rte=0 → pev 0x0a → adapter → `lcb` with index 0 → phone list event as above. Same on both.
- RESULT: index did NOT change after the slide (still 0) on either image. NOT confirmed: whether the selection moves on the display, because the list adapter only forwards input events and the actual LVGL scroll happens elsewhere. In the first run the single followed the slide within ~1 s; with a 1 s wait the scroll animation may still have been running (adapter skips when handle+0x57c==1). Next: wait longer (3-5 s) between slide and tap, or read the list's selected index via a RAM dump.
- sie arg value 0xc33c0001 (ours) vs 0x30a40001 (stock) differs in the high half only. GUESS: a pointer (name or buffer), not data.

LVGL page events 0x1a/0x1f/0x20/0x21 (ours fewer than stock), seen in all runs. Counts per run (ours/stock): t1 16/24; ns 15/23; sl/sw 24/40. The four codes always have identical counts within an image, the ratio isn't constant, and 0x2b/0x2c/0x34 are exactly equal. GUESS: a per-draw-cycle group whose count depends on render timing (ours' scheduler and GPU interrupt cadence differ), not on firmware behavior; and 0x1a/0x1f/0x20/0x21 are not EvenHub codes (the handler uses 0x0a/0x42-0x4f). Mapping to LVGL names is unverified: LVGL version not recorded in lv_conf_recovered.h. Not resolved.

#### Slide-wait-tap: why the index stayed 0 (runs x68/xstk, y68/ystk, z68; slideL x2 and x1, 4 s waits)
- Hooks on `common_list_container_inject_event` (ours 0x5760f8, stock 0x4de354, r0 = list, r0+0x5c = current_index): the list `lst` is the 2-item Rebuild(menu) one (cnt=2, visible=4, anim_busy=0, event_cb non-null). Every DOWNROLL (rte=5 → page 0x45 → inject event 1) reaches it with idx=0 and leaves idx at 0; no focus-style update follows (z68: no `update_focus_style` hit after ev=1). Same on both images.
- Cause (source reading): evenhub_ui_page.c maps SCROLL_UP → 0 and SCROLL_DOWN → 1, but common_containers_private.h has COMMON_LIST_EVENT_DOWN=0, UP=1. So a DOWNROLL injects UP: at idx 0 it only starts a rubber-band animation. Either the swap is how the firmware really behaves (UPROLL = move to next item) or one of the two decompiled enum names is mislabeled (GUESS; not checked against the binary).
- Next: slide with UPROLL (report 0x40 → rte=4 → page 0x44 → event 0) then tap; expect idx 1. Runs r68/rstk.

#### CONFIRMED: slide then tap changes the list index (runs r68 / rstk; GPUJIM NOSILENT TOUCHONLY; slideR 0x40 diffX 10, release, wait 4 s, single, release)
- UPROLL (rte=4) → page 0x44 → inject event 0 (list DOWN): idx 0 → focus style updated (ufs=1) on both arms, both images.
- Tap (rte=0 → page 0x0a): inject event 2 sees idx=1; `common_list_event_callback` gets selected_index=1.
- Phone notification on both images: `aa12..0101e001 08 02 6a 0b 0a 09 08 03 12 03 "lst" 20 01` = ListEvent{container_id=3, container_name="lst", item_index=1} (event_type 0 = click, omitted). item_name (field 3) is absent; GUESS: the sender doesn't encode it for this path (unchecked).
- Ours vs stock masked notifs identical except idx 1 and 4 (heartbeat counters).
- Open: with DOWNROLL (slideL) the index stays 0 (see above). Whether that direction swap is real firmware behavior or a mislabeled decompile enum is a guess; the ring semantic (which slide = next item) is unverified on hardware.

## Wave-23 follow-up (enum direction, LVGL events)
- List direction enum: the SLIDE_L/SLIDE_R -> list UP/DOWN swap is real firmware behaviour. Stock shows the same index movement in the sim (UPROLL 0x40 moves the index 0 -> 1 on both images). Which enum name is "correct" is cosmetic and unchecked.
- LVGL page-event 16 vs 24: the codes 0x1a/0x1f/0x20/0x21/0x2b/0x2c/0x34 are probably the LVGL 9.3 per-draw-pass events (GUESS: the build does not record the LVGL version). The ours-to-stock difference is a multiple of 8, not a constant ratio. The timeline check (pev=1a against rfl/rbd/uicb) is not done.

## Wave 24 note
Wave 24 changed no apollo-main source (only em9305 ARC sources, `sources.json` `not_built`, docs and coverage tooling). The apollo image is unchanged, so no new paired sim was run; the sim68 (ours) vs stk12 (stock) GPUJIM=1 results stand.

## 2026-10-31 — jimrandomh emulator: current build (final2-1030) vs stock 2.2.6.10

**Setup.**
- Emulator: `~/Repo/jimrandomh/g2-firmware-emulator`, master f30527c, which equals upstream master. Renode was built from the pinned commit e8c7c2d with `scripts/bootstrap-renode.sh` on macOS arm64; the build is in the checkout's ignored `vendor/` and `tools/`.
- GPU and UI runs use a separate worktree, `~/Repo/jimrandomh/g2-firmware-emulator-jimdev`. It is upstream `jim-emulator-dev` 9a19857 (James Babcock's GPU general pipeline and live UI) plus the 3-bit RING_STOP fix. The master checkout is unchanged apart from ignored files.
- Harness: `generated/opencfw/runsim.sh` (copied from the old checkout) and `.waves/sim-fix/hub/hubsim.py`. The emulator path is now `$G2EMU`, defaulting to the jimrandomh checkout.
- New for this run:
  - `generated/opencfw/bootrun.sh` boots the bootloader-entry board (`g2emu.ota_boot_profile` template from the stock 2.2.6.10 container) with any bootloader/app pair and records the UART1 console.
  - `build/simota/pack_main.py` packages an app into an EVENOTA.

**Single-temple boot, 20 s (display profile).** Run names: `stk12`, `f1030`, `ldfix`.

| | stock 2.2.6.10 | ours final2-1030 | ours + linker fix |
|---|---|---|---|
| HCI host packets + latched frames | 60 lines | identical to stock | identical to stock |
| Frames | 2, sha256 0c5cc90b… | same | same |
| Faults / watchdog / asserts | 0 | 0 | 0 |
| Warnings | JBD 0x9F fixture, GPU ring-stop | same two | same two |

**Bug found and fixed: writable named sections were never initialised.**
- `g2-apollo-main.ld` copied only `__data_start..__data_end` (ending at 0x20017ad0).
- 0x14aa4 bytes of writable orphan sections were placed after it, at 0x20017ad0..0x2002c574, with their own LMAs. These are the eight lv_i18n locale pointer tables `.g2_locale_data_*` (`display_context_registry.c`), all `.g2_conversate_*_2xxxxxxx` state, `.g2_bss_*` and `.g2_pdm_clock_pin_words`.
- Startup never loaded them. In the sim, 0x20026c50 (the `en` table), 0x20026ec4 (`de`) and 0x20017ad0 read 0 at t = 3 s.
- Fix: `.data` now also collects `INPUT_SECTION_FLAGS (SHF_WRITE) *(.g2_*)`, which gives one contiguous copy row ending at 0x2002c574.
- After the fix the sim reads 0x007B1268 / 0x007AC360 / 0x007B0BB3 / 0x007A9658, which match the ELF initial bytes. Code addresses do not change. The relink has 0 undefined references and `make sources-check` passes.

**Bootloader entry, 20 s** (`bootrun.sh`; secure mask ROM not modelled):

| bootloader + app | HCI + frames | CFSR | Result |
|---|---|---|---|
| stock + stock (`sbsa`) | 59 lines | 0 | baseline |
| ours final2-1030 + stock app (`obsa`) | identical | 0 | hands off; same as stock |
| ours + ours with linker fix (`oboa`) | identical (repeat counts aside) | 0 | hands off; same as stock |

**OTA packaging.** `pack_main.py` given stock's own app reproduces the stock container byte for byte. Our container (`build/simota/opencfw-main-ldfix.evenota`, 4,605,259 B) passes `g2emu.firmware.validate_g2`.

**Paired EvenHub + touch** (`hubsim.py`, jimdev worktree, `PAIRED=1 GPUJIM=1 WIDE=1 LISTPAGE=1 NOSILENT=1 TOUCHONLY=1`, TOUCHX slideR / release / wait 4 / single / release). Runs `li2-stk12` and `li2-ldfix`, executed one at a time.
- Both: Secure Connections pairing completes and the link is encrypted. All 18 phone steps return the same per-step notification counts.
- Touch: the slide gives 0 notifications and the tap gives 1, on both.
- 22 notifications each. With byte 2 and the CRC masked they match, except idx 1 and 4, the known heartbeat counters.
- The last frame is byte-identical on both: ListEvent{container 3 "lst", item_index 1}. CFSR/HFSR are 0 on both.
- Note: running 5+ paired Renode instances at once on this 10-core host starved them (spin-yield sync at a 10 µs quantum). Run paired cases at most two at a time.

**Live-UI walk, both lenses** (jim's `g2emu.live` engine, with a `--firmware` option added in the jimdev worktree; script `generated/opencfw/uishots.py`). The sequence is boot from erased NOR, wake (double tap), slide right ×2, tap-then-long (app menu), then release.
- All 12 final lens captures for ours (`ui-ldfix`) are **pixel-identical** to stock 2.2.6.10 (`ui-stk12`).
- Neither image had a GPU fault or unsupported draw.
- Ours reaches the same frames with fewer GPU draws and panel latches (wake: 0x30f vs 0x53a draws, 46 vs 52 latches), so it renders fewer intermediate animation frames. This is a timing difference, not a pixel difference. It is not investigated; check animation smoothness on hardware.

**Simulated OTA install, stock 2.2.6.10 → ours → stock** (`g2emu.ota_probe --boot-mode bootloader-entry --component 5 --followup <stock>`; run `ota-stock-ours-stock`, 5,051 s wall).
- First leg, against the final2-1030 image with the linker fix:
  - Real ATT/SMP Secure Connections.
  - Stock's OTA receiver accepted all 935 MAIN blocks and END.
  - The stock bootloader installed it: "updata firmware success … APP jumpaddr = 0x5937b5". Installed MRAM equals our image (sha256 9012744…).
  - Ours booted, initialised the EM9305 and advertised again. CFSR/HFSR 0; OTA flag cleared.
- Return leg **failed**: "Installed candidate failed to authenticate the original retained phone key". The encryption observation is [0, 6], i.e. HCI 0x06 PIN or Key Missing.
  - Cause: `audio_ble_privacy_nvm_records`, the Cordio app_db bond rows that stock keeps at mapped MRAM 0x7ff000, was linked into SSRAM .bss at 0x201ff8c0.
  - The `display_ble_mram_records_7ff000.ld` fragment was never included, so `*(.bss.*)` captured the section.
  - Effect on hardware: bonds made by stock are invisible, and our own bonds would not survive a reset.
- Fix: `g2-apollo-main.ld` now places `.bss.opencfw.mram.records` at 0x007FF000 (NOLOAD, asserted 0xA00 bytes), beside the OTA-flag page. Image size is unchanged; the symbol is now at 0x007ff000.
- The other unincluded `.ld` fragments were checked:
  - `*_noload` / `*_noinit` cells already land in the main script's NOLOAD `.noinit`, which is not zeroed.
  - The OTA flag is pinned by the main script.
  - The rest pin RAM cells to stock addresses, which is no longer required.

**Round trip #2 (bond-page fix, `ota2-stock-ours-stock`).**
- First leg passed as before.
- On the return leg the retained phone key now authenticates on ours: encryption observation [1, 0].
- Our OTA receiver then answered START with status 10. Hooks (`EXTRA_MONITOR`, an opt-in addition to `ota_probe.py` in the jimdev worktree) traced it:
  - `_otaFsHealthCheckAndHeal` → `_otaFsHealthProbe` → `file_open("ota/_health_probe.bin","wb")` returned NULL, even after a littlefs format.
  - `osMutexAcquire` returned 0xfffffffc (osErrorParameter) on every file open, because the file-API mutex handle was NULL.
- Cause: stock RAM 0x200748f4 is one cell. `redirect_init` (0x474d9c) stores the redirect mutex there, and `file_open/read/write/close` lock it. Our build had two objects for it: `g2_codec_redirect_mutex` (written) and `audio_file_api_mutex` (read, never set). **So every file-API open failed in our firmware.**
- Fix: `audio_file_api_mutex` is now an alias of `g2_codec_redirect_mutex` (`storage/file-redirect/file_redirect_mutex_ram.c`). Fresh full build `build/mutexfix2`: 2717/2717 compiled, 0 undefined.
- A bounded probe on the new image (`ota-ours-start4`) has our receiver accept START and the first 3 blocks of a stock image.
- A static rescan of stock-RAM-tagged objects (1,269 cells) finds no other split cells. Untagged duplicates like this one are only visible at runtime.

**Round trip #3: full success** (image `build/mutexfix2-link`, all of today's fixes; container `build/simota/opencfw-main-1031.evenota`; run `ota3-stock-ours-stock`, 11,025 s wall).
- Stock 2.2.6.10 → ours: 935/935 blocks accepted. The stock bootloader installs ours, which boots and advertises. Installed MRAM equals our image.
- Ours → stock (same live device, retained bond):
  - Encryption with the original phone key succeeds ([1, 0]).
  - Our OTA receiver accepts START, all 861 blocks and END.
  - After reset the stock bootloader checks the CRC (`calc CRC = 0xc91081df(0xc91081df)`), installs, and jumps to the stock app (0x5e4233).
  - Installed MRAM equals stock (sha256 19044a72…). It advertises; CFSR/HFSR 0; OTA flag cleared.
- The probe's `complete_ota_qualified=false` / `installed_and_booted=false` reflect its policy: an image hash with no registered trace profile is diagnostic only. It is not an observed failure.
- The same build still matches stock in the 20 s boot comparison (HCI stream and frames identical) and in all 12 live-UI lens captures.
- Paired phone/touch regression on the same build (`li2-m1031`): every step matches stock. Of the 22 notifications, only the known heartbeat counters (idx 1 and 4) differ. CFSR/HFSR 0.

**Not covered by the simulator:** the EM9305, codec, touch and case images (the emulator models those chips rather than executing them), physical timing, RF, display optics, and power draw.
