# G2 Apollo main hardware-driver findings (2.2.6.10)

Recovered on 2026-10-21 while reconstructing the Apollo main hardware drivers as C under
`g2/src/apollo-main/drivers/`. Evidence comes from the locked 2.2.6.10 main image: the raw Ghidra
corpus (`g2/research/corpus/apollo-main/ghidra/open-2026-09-29/`), GNU objdump of the stock bytes,
and REA 7aa4d768 with the Ghidra 12.1.4 provider (see [Tooling](#tooling)). Addresses are main-image
runtime VAs (file offset + 0x437fe0). These are static readings of the stock code. None of them
proves hardware timing, and none of the C is byte-identical to stock.

The later sections (board configuration onwards) merge the hardware-relevant results of the
2026-10-21 reconstruction waves. Values marked "initialised data" were read from the decoded
`.data` image (0x20000000, 0x4558 B, decoder 0x43A11E). Inferences are marked INF.

## Product I2C HAL (`driver/hal/src/hal_i2c.c`, 0x50412C..0x50475B)

- Eight logical buses map one-to-one to IOM modules. The bus table is in initialised RAM at
  0x20000C4C: 16-byte rows `{module, handle, pins*, am_hal_iom_config_t*}`, where `pins` is
  `{scl, sda, scl_cfg, sda_cfg}`. Per-bus mutexes are at 0x200738FC. Only IOM4 runs interrupts:
  IRQ 10, mask 0xFF, and `hal_i2c_irq_handler` services the IOM4 handle. IOM4's semaphore is at
  0x2007460C.
- Every transfer runs the same sequence:
  1. Take the bus mutex.
  2. Wake the IOM (`power_ctrl(WAKE)`, up to 1000 retries with 10 ms delays) and restore the pins.
  3. Run one or two blocking transactions.
  4. Return the IOM to deep sleep. Bus 4 also parks its pins on the disabled pad config at ROM 0x78EE48.
  5. Release the mutex.

  Despite their stock names, `hal_i2c_power_down` and `hal_i2c_power_up` are the wake and sleep
  halves of that sequence.
- `hal_i2c_transfer_full` sends a write and then a read as two separate transactions, with
  `bContinue = 0`, so there is no repeated start. `hal_i2c_transfer_joined` concatenates up to
  32 bytes into one write. The transaction priority byte (+0x22) is always 1.
- The IOM HAL island `[0x55BCE8, 0x55D280)` was already reconstructed in `g2/src`, but under BLE
  and radio names (`audio_ble_radio_stack_open_55c2bc` = `am_hal_iom_initialize`,
  `audio_ble_radio_stack_option_55c7e8` = `power_ctrl`, `audio_ble_radio_stack_config_55ca94` =
  `configure`, `audio_ble_radio_stack_start_55c32e` = `enable`,
  `audio_ble_vendor_receive_55cc1c` = `blocking_transfer`). The I2C callers above confirm their
  roles. Still missing as C: `interrupt_enable` 0x55C498, `interrupt_status_get` 0x55C4D0,
  `interrupt_clear` 0x55C518, `interrupt_service` 0x55C558 and the helper at 0x55C174. Stock
  predates SDK 5.2, so compiling the pinned AmbiqSuite 5.1.0 `am_hal_iom.c` alongside the island
  would duplicate it rather than replace it.

| Bus | IOM | Pads (SCL/SDA) | Clock | Devices |
|---|---|---|---|---|
| 2 | IOM2 | GPIO25/26 | 400 kHz | TI OPT3007 ALS @0x45 |
| 4 | IOM4 | GPIO34/35 | 1 MHz | TDK ICM-45608 IMU @0x69 (IRQ-driven) |
| 5 | IOM5 | GPIO47/48 | 400 kHz | PSoC 4000T touch @0x0C |
| 7 | IOM7 | GPIO22/23 | 400 kHz | Nordic nPM1300 PMIC @0x6B, TI BQ25180 charger @0x6A, TI BQ27427 gauge @0x55 |
| — | IOM6 (SPI) | internal | 16 MHz | EM9305 BLE controller HCI (see [BLE](#ble-host-to-em9305-controller)) |

- Bus table rows (initialised data at 0x20000C4C): module = bus number for all eight rows; only
  buses 2, 4, 5 and 7 have pins and a config. Pin rows are ROM 0x786020/30/40/50, pad config word
  0x4200 for both lines.
- IOM configs: buses 2/5/7 share 0x20000C0C (I2C, 0x61A80 = 400 kHz); bus 4 uses 0x20000C38
  (I2C, 0xF4240 = 1 MHz, command-queue buffer 0x2035CE18, 0x800 B).
- The SCL/SDA order is the reconstruction's field naming in `hal_i2c.c`; the pads themselves are
  read from ROM.
- IOM6: `0x4B48A6` calls `0x52DD94(6, …)`, which calls `am_hal_iom_initialize`. Its config at
  0x200001B4 is SPI, 16,000,000 Hz, SPI mode 0.

## Board configuration, GPIO table and hardware ID (`product\s200\app\config\board_config.c`)

- `board_init` 0x5093AC runs these steps in order:
  1. Pin table (0x53A454).
  2. Empty hook 0x509132.
  3. HW-version detect 0x509134.
  4. UART channels (0x55E388).
  5. `HAL_I2CInit`.
  6. `hal_uart_power_on(1)` (0x55E5BC).
- Board info is 4 B at RAM 0x20074368: +0 charger family (1 nPM1300, 2 BQ25180 + BQ27427),
  +1 hw_version, +2 u16 mV. This RAM is zero-initialised.
- Selector 0x50938E returns pointers into board info: arg 1 gives 0x20074369, arg 2 gives
  0x2007436A, and args 0 and ≥3 give 0x20074368. The only literal for the cell is at 0x509494.
- HW-ID input: GPIO16, ADC slot 3 (single-ended channel 3), three matching samples,
  mV = sample × 1190 >> 12. Pin configs are ROM 0x78EE8C (ADC) and 0x78EE90 (released).
- HW-ID bins: 950–1050 mV → 6; 550–650 → 3; 300–400 → 4; 100–250 → 5; anything else → 0xFF.
  The float thresholds are at 0x509448..0x509464.
- Every bin writes charger family 1. No caller of 0x50938E writes the byte.
  - INF: the BQ25180 + BQ27427 path (`power_init` 0x5093D4, family 2) is unreachable in 2.2.6.10.
  - If ADC detection fails, the byte stays 0 and no charger driver starts.
- CLI `hardware_version_string` 0x57E6CC names hw_version codes: 1 EVT1, 2 EVT2, 3 EVT3, 4 DVT1,
  5 DVT2, anything else "Unknown". The ADC bins produce only 3–6, so 6 prints "Unknown".
- `power_init` 0x5093D4 brings up the charger: family 1 → `npmx_main_driver_init` 0x512644;
  family 2 → `DRV_Bq25180HwInit`, then `DRV_Bq27427HwInit`.
- Board pin table: ROM 0x686DB8, 0x61 rows × 12 B `{pad u32, mode, level, int_dir, pad, handler}`.
  - Modes: 1 output, 2 input, 4 disabled. Mode 3 rows are left to their peripheral driver.
- Pin-table interrupt inputs (handlers on GPIO channel 0, IRQ priority 4):

  | Pad | Handler | Role |
  |---|---|---|
  | GPIO4 | 0x510FD8 | sits just before the npmx glue (INF: nPM1300 GPIO1 IRQ) |
  | GPIO27 | 0x55BA64 | touch attention; calls `input_msg_send_touch` 0x513056 |
  | GPIO29 | 0x57A80E | GX8002 event line |
  | GPIO38 | 0x4A6AE8 | IMU INT1 data-ready |

- Pin-table outputs:
  - Initially high: GPIO9, GPIO10 and GPIO134 (the shared codec/sensor rail).
  - Initially low: GPIO7, 11, 45, 68, 128, 129, 142, 143, 144, 146 and 147.
- Pin-table mode-3 (peripheral) pads:
  - I2C: 22/23, 25/26, 34/35, 47/48.
  - MSPI1: 49, 95–98, 103. MSPI1 DQS (GPIO104) is mode 4, disabled.
  - PDM: 50/51.
  - Buzzer: 145.
  - Unassigned: 64–67, 69, 72, 73 (INF: MSPI0 panel pads).
- Logical "codec GPIO" channels used by drivers map to pads as follows:
  - Channel 6 is GPIO134.
  - Channel 9 (ALS rail) is also GPIO134.
  - GX8002 power uses GPIO134 → GPIO143 → GPIO146, which matches the older notes' logical channels 6/7/8.
  - The IMU rail is channel 1 and touch reset is channel 10. Their pads are not resolved here.
- UART channels (table at RAM 0x20000D2C):
  - IRQ = module + 15.
  - Priority is 3 for channel 0 and 4 for the other channels.
  - The RX buffer is 0x400 B.
  - Roles: UART0 (0x40039000, IRQ 15) is the left/right sync link. Channel 1 is the console/CLI.
    Product UART 2 is the charging case. UART3 (0x4003C000) is the GX8002 link.
- ADC: AmbiqSuite 5.1.0 `am_hal_adc` at 0x55D94C..0x55E09C is linked unchanged. ADC base is
  0x40038000. The INFO1 trim cache is at 0x20071948 (magic 0x1F01600D).
- IOM handle state offsets:

  | Offset | Field |
  |---|---|
  | +0x14 | user INTEN |
  | +0x18 | accumulator |
  | +0x28 | callbacks[256] |
  | +0x828 | cmdq |
  | +0x83C | bHP |
  | +0x854 | HP entries, 32 B each |

  After every write to INTCLR, the code reads INTSTAT back.

## Boot, reset, watchdog and power modes

- Reset vector slot 1 (ROM 0x438004) = 0x5E4233. The handler 0x5E4232..0x5E4241 sets
  MSPLIM/PSPLIM = 0x2007D000, then jumps to the IAR program entry 0x5E4254.
  - The inventory sizes this handler as 2 B, which is wrong.
  - Unused vectors point to `am_default_isr` 0x5E4250 (`b .`). The NMI handler is 0x4397A6.
- IAR data init: scatter decompressor 0x43A11E, records `{src offset, len<<1|flag, dst}`.
  - `.data`: 0x4558 B to 0x20000000; zero-init starts at 0x20004558.
  - The large record at 0x75D400 expands 0xBBE6E B to 0x20080000.
  - The init table is at 0x75D3C8; the token format is under [Cross-cutting](#cross-cutting).
- `main` 0x5CE01E is reached from 0x5E42AA:
  1. 200 ms delay.
  2. Auto-init table runner 0x5BF0BC.
  3. ">>> SYSTEM BOOT START <<<".
  4. Reset-reason report 0x5CDD6C.
  5. Build banner.
  6. `task_vote_init`.
  7. `kernel_start` from thread-manager record RAM 0x200040D8 (never returns).
- Auto-init table: ROM 0x6D1E0C..0x6D1EC3, 23 × 8-B `{fn, priority}`.
  - The runner copies at most 256 entries to RAM 0x20066A30, sorts them by ascending priority
    with IAR qsort, and calls each non-NULL entry.
  - Comparator 0x5BF0B4.
- `board_init` 0x5CDD14 is the priority-0 entry (row 0x6D1E2C = {0x5CDD15, 0}). Its steps, in order:
  1. Latch RSTGEN status into `g2_reset_status` (a 16-B `am_hal_reset_status_t`, IAR layout).
  2. Start the MCU watchdog (0x4B29D8).
  3. FPU enable and lazy stacking.
  4. Low-power init (0x4C2AE8).
  5. I-cache and D-cache (0x474F32).
  6. HIGH_PERFORMANCE MCU mode (0x47F0A0).
  7. Heap init (0x4842E6).
  8. NemaGFX GPU init (0x59FAE0).
  9. CmBacktrace init.
- The stock pwrctrl MCU-mode switch 0x47EF74 predates the pinned AmbiqSuite 5.1.0.
- SPOT manager settings: the build has NO_TEMPSENSE_IN_DEEPSLEEP=0 and
  AM_HAL_PWRCTRL_SIMOLP_AUTOSWITCH=1 (am_hal_spotmgr 0x4801FC..0x48041E).
- MCU watchdog config (initialised data 0x20000950): {clock LFRC/64 (2), interrupt off,
  interrupt value 12, reset on, reset value 480}. This gives about a 30 s reset at 16 Hz.
  - Callees: `am_hal_wdt_stop` 0x52A38A, `config` 0x52A2D8, `start` 0x52A32C.
  - The restart hook is 0x4B29F8.
- External watchdog: `watchdog_enable` 0x52F2E0 arms the nPM1300 watchdog (`npmx_watchdog_enable`
  0x511882) only when the board family byte is 1. It is called from `DEV_Init`.
- Reset-reason priority: EXT, POR, BOD, SWPOR, SWPOI, DBGR, WDT, AIRCR, then unknown.
  - A brown-out reset is answered at once with a software POR (`AM_HAL_RESET_CONTROL_SWPOR`).
    This is firmware policy (0x5CDD6C).
  - An external-pin reset (RSTGEN STAT bit 0) makes the input thread play buzzer effect 8.
- Build identity:
  - Git describe `master:v2.2.6.10-0-gb79923a139f5` (0x756930). Built `Jul  6 2026 21:37:52`.
  - Banner "Start up S200 EVT Project.".
  - CmBacktrace code range is 0x438400..0x5FA056.

## Drivers

### nPM1300 PMIC, charger family 1 (`driver\npmx_driver_transplant\src\npmx_main_driver.c`, 0x511002..0x512BB1)
- I2C bus 7 at 0x6B, the same bus as the BQ25180 and BQ27427. Register addresses are 16-bit and sent high byte first.
- npmx calls return 0x2BAD0000 on success, +1 for INVALID_PARAM and +2 for IO.
- Interrupt: nPM1300 GPIO1 is the IRQ output.
  - Enabled events: watchdog warning, VBUS detected and VBUS removed.
  - VBUS events drive case detection (`box_detect_vbus_connected` 0x4AC130, `_removed` 0x4AC154).
- Charger settings:
  - Charge 96 mA; discharge limit 1000 mA.
  - Termination 4450 mV normal, 4000 mV warm.
  - VBUS limit 500 mA.
  - NTC 100 kΩ, β 4250.
- Rails: BUCK2 at 3.1 V and LDSW1 used as an LDO at 1.8 V. The nPM1300 watchdog is about 30.7 s
  in reset mode (timer mode 2, config ROM 0x78B624).
- SYSLABEL register 0x0101: a value of 0x00 or 0xFF is replaced by 0x13.
- npmx instance record (0xD0 B): callbacks at +0x98, event masks at +0xC4.
  - Charge current is 32..800 mA in 2 mA steps (register 0x308).
  - Discharge current is code × 3.23 mA.
- Upstream code:
  - npmx v1.0.1 core/gpio/vbusin/timer/charger/adc/buck/ldsw/backend/ship: 0x55EA40..0x55FC6A.
  - `npmx_errlog` 0x58EA08..0x58EA68.
  - The hand-written `npmx_core.c` should be compared against the now checked-out submodule
    `e1aaec53`. Some leaves also exist as `display_driver_uled_pmic_*`.
- Battery gauging uses Nordic's closed `nrf_fuel_gauge` (see [Licence-blocked libraries](#licence-blocked-libraries-identified)).
  Its telemetry goes into the shared record at RAM 0x20073B18.
- `npmx_main_driver_init` checks hw_version == 6 for a variant path (0x512644).

### BQ25180 charger (`driver/chg/drv_bq25180.c`, 0x53A670..0x53AF4B)
- I2C bus 7, address 0x6A. Writes use `hal_i2c_transfer_joined` with the result ignored. Reads use `hal_i2c_transfer_full`, and the receive byte is not pre-cleared, so callers' `<0` checks never fire. The log tag is spelled `bp25180`.
- Device ID check (0x53A9D0): MASK_ID (0x0C) `& 0xF` must equal 0. A raw value below 1 returns -1.
- `bq25180_apply_defaults` makes 19 calls. The resulting register image for 0x00..0x0C is `00 00 00 5A 24 24 1F 44 06 00 21 00 F0`:
  - VBATREG 4.40 V; ICHG code 0x24 (90 mA); ILIM code 6, which is **700 mA** even though the argument is 1000.
  - ITERM 10 %; IPRECHG 2×ITERM; IBAT_OCP 500 mA; SYS_REG 4.4 V; VINDPM 4.5 V.
  - BUVLO 2.8 V; VLOWV 2.8 V; VDPPM disabled; safety timer 6 h; watchdog 160 s.
  - All seven interrupts masked; charging enabled last.
- ReadStatet packs STAT0 into bits 0..7 and STAT1 into bits 8..14 (reserved bit 5 dropped). It caches CHG_STAT at RAM 0x20073B18. RefreshStatus stores the FLAG0 image at runtime+0x14 and the status word at +0x16, where the runtime record is at RAM 0x200744FC.

### BQ27427 fuel gauge (`drv_bq27427.c`, 0x53AFC0..0x53C1C3)
- I2C bus 7, address 0x55.
  - A 16-bit read is two one-byte reads, combined little-endian. The HAL status is ignored, so callers' `< 0` checks never fire.
  - `write_block` always returns 0.
- Unseal key 0x80008000 (RAM 0x200006E8, initialised data); Seal is Control 0x0020.
- CFGUPDATE: Control 0x0013. The exit is SOFT_RESET 0x0042. It polls Flags bit 4 every 25 ms, up to 100 times, and a timeout is not reported.
- Data-memory descriptor table at RAM 0x200006EC: 7 × 8-byte entries `{subclass, offset, size, pad, min, max}`; the min/max fields are never read.
- Values written by `configure_from_params`:
  - Design Capacity 80 mAh, Design Energy 240 mWh, Terminate Voltage 3100 mV (initialiser at ROM 0x78A8BC).
  - Update Status 3; subclass 64 byte 4 = 0x2B; subclass 105 byte 5 = 0x28.
  - All writes go through a dirty-gated block commit, then the gauge is sealed.
- Chemistry is always switched to CHEM_B (Control 0x0031), with no check of the current CHEM_ID. The 0x0031 → 4.2 V 0x1202 mapping comes from TRM recollection and is unverified.
- Status refresh publishes into the shared telemetry record at RAM 0x20073B18:
  - +0 BQ25180 CHG_STAT, +4 SOC, +8 voltage in mV, +0xC average current, +0x10 (Temp − 2731) × 10.
  - Flags reading 0, or low byte 0xFF, means no gauge and returns -1.
- The gauge is brought up only when the board-config byte is 2 (0x5093D4: `DRV_Bq25180HwInit` then `DRV_Bq27427HwInit`).

### Charger common / battery sync (`platform/service/charger/charger_common.c`, `callback_mgr/cb_charge.c`, `ring_battery/service_ring_battery.c`)
- Left/right battery sync record: 12 bytes on sync service 0x105.

  | Offset | Field |
  |---|---|
  | +0 | msg_id |
  | +1 | length (8 or 0) |
  | +2 | sender role |
  | +3 | destination role |
  | +4 | int32 SOC |
  | +8 | int8 charging |

- Message IDs: 1 REQUEST, 2 RESPONSE, 3 NOTIFY, 4 REQUEST_NOTIFY, 5 ring battery update, 6 ring battery request. The handler is 0x5F958C, which rejects records under 12 bytes.
- SOC rules:
  - A SOC is valid when it is below 101 unsigned, so the −1 sentinel is invalid.
  - Aggregate SOC = min(local, peer).
  - Local SOC compensation near full: 93→93/94, 94→95/96, 95→97/98, 96→99, ≥97→100.
  - Local charging means AverageCurrent < 0.
  - At SOC ≥ 98, a change in the charging flag must persist for 4 polls before it is accepted.
- Startup sync retries at polls 2/4/6/8 and gives up at poll 16.
- Callback managers are linked lists, not fixed tables: BAT_INFO at 0x20073F78, RING_BAT_INFO at 0x20073F90. Event 0 = SOC, event 1 = charging.

### Audio capture drivers (`driver/codec/drv_gx8002b.c`, `driver/pdm/drv_pdm.c`, `drv_pdm_production.c`)
- **Interrupts:** I2S0 is IRQ 44 and PDM0 is IRQ 48, both at priority 4.
- **GX8002 power sequence:**
  - On: GPIO134 → 5 ms → GPIO143 → 20 ms → GPIO146. The selector is at 0x509024.
  - Off: all three lines drop with no delays.
  - Reboot: off, 100 ms, on, then +1500 ms unless the argument is nonzero.
- **GX8002 I2S link:**
  - The GX8002 is I2S clock master. Apollo I2S0 is an RX-only slave.
  - Format: 2 channels, 32-bit slots, data delay 1, 16-bit samples.
  - Ping/pong DMA at 0x20364E18 / 0x20365A98, 3200 B per block. Bit 4 (RXDMACPL) posts audio message type 2.
- **PDM:**
  - Config (28 B at RAM 0x20000900 / 0x20000928): MCLK divide by 15 (24 MHz HFRC → 1.6 MHz), +1.5 dB gain, SINCRATE 25, HPF code 3, mono left, PCM packing.
  - Pads GPIO50/51.
  - Normal DMA blocks are 640 B; production blocks are 6400 B. 24-bit words are reduced to 16-bit PCM (bits 23..8).
  - PDM0_IRQHandler routes to the production handle when `productModeGet()==1` and byte 0x20075019 is 0.
  - 0x20075019 is the aging/production-test flag. Its existing names `g2_audio_pdm_variant` and
    `g2_pdm_production_bypass` are misleading.

### GX8002 host link (`driver/codec`, 0x57BA88..0x57DAxx) and audio thread (0x53C2BE..0x53CE72)
- **Transport:** UART3 (0x4003C000) at 115200 baud, opened and closed around every transaction.
- **Frame header (14 B):**

  | Offset | Size | Field |
  |---|---|---|
  | +0 | 4 | magic `BUXX` |
  | +4 | 2 | cmd, little-endian: low byte TYPE, high byte NR (1 request, 2 response, 3 event) |
  | +6 | 1 | sequence |
  | +7 | 1 | flags (bit 0 = body CRC present) |
  | +8 | 2 | body length |
  | +10 | 4 | CRC-32 (zlib) over bytes 0..9 |

  - The body is at most 16 B. Responses are not matched to the request's sequence number.
- **Commands** (type byte):

  | Cmd | Function |
  |---|---|
  | 0x02 | version |
  | 0x07 | BF mode |
  | 0x08 | wakeup mode |
  | 0x0B | mic gain, 0..48 |
  | 0x0C / 0x0D | DMIC open / close |
  | 0x0E | MicDelay1Bit, a fixed raw frame |
  | 0x0F | I2S output |
  | 0x70 | mic state |

  - Events: 0x030C wake word; 0x030D VAD (1 voice, 0 silence). They are signalled by the codec pulling Apollo GPIO29 low.
  - Requests are tried 3 times; the SVC wrappers use a 200-tick timeout.
- **Audio thread:**
  - Thread "audio": priority 47, 8 KB stack at 0x20360E18.
  - Queue: 50 × 12-byte messages. Dispatch table at RAM 0x20003FBC: 0 CodecCtr, 1 PdmCtr, 2 DmaInt, 3 PDM data, 4 codec check, 5 IntNotify, 6 AudioCheck, 8 PeerSync.
  - Watchdog: if fewer than 20 I2S blocks arrive in 2000 ticks, the thread reboots the codec. The check runs on the one-shot timer `codec_audio_check`.
- **Codec-side behaviour:**
  - Image A alone handles 0x07, plus 0x09/0x0A/0x71, which the host never sends.
  - Image B alone handles 0x08.
  - protocols.md lacks the 0x03xx events and the reply-command rule.

### GX8002 firmware update (`platform/audio/service_codec_dfu.c`, 0x577D7C..0x57A35F)
- The package is `/firmware/codec.bin`, an FWPK container whose records are
  `<type, size, offset, crc32>`. Type 1 is the boot container and type 2 is the flash image.
- The boot header is the lvp_kws 32-byte struct. Its four u32 fields are big-endian.
- Bring-up:
  1. Open UART3 at 230400.
  2. `DRV_Gx8002_Reboot(1)`.
  3. Send 0xEF every 1 ms, up to 10001 tries, until `M` arrives.
- Stage 1:
  1. Send `Y` and the word count, then the image in 256-B writes.
  2. Wait for `F`, then `wfb`; send `OK`.
  3. Send the stage-2 baud and switch the Apollo side.
  4. Wait for `GET`; send `OK`.
- The stage-2 baud sent is always 1,000,000. The header's 1.5 Mbaud value is only logged.
- Stage 2:
  1. Send `S`, the checksum and the size.
  2. Wait for `ready`, then send the body.
  3. Wait for `O`, then `boot>`.
- Flash:
  1. Send `serialdown 0 <size> 8192\n` and the CRC-32.
  2. For each 8192-B chunk: wait for `~sta~`, send the chunk, wait for `~fin~`.
  3. Finish on `[Result]:`, then `SUCC`.

### LC3 encoder (Google liblc3 v1.1.3 `96a3af0b`, `LC3_PLUS_HR=1`)
- `ltpf.c` and `bits.c` are at 0x438400..0x439B78. They use the generic C path (`ltpf_arm.h` is
  disabled), and IAR auto-vectorised them with MVE. Decoding them needs
  `objdump -marmv8.1-m.main`.
- `sns.c`, `tns.c` and `spec.c` are at about 0x5990CC..0x59C78C, in that link order.
- The upstream non-const tables `q_thr`, `q_inv` and `ge_table` are in RAM at 0x20004144,
  0x20004164 and 0x20003A78.
- `lc3_setup_encoder` is 0x591374 (existing name `audio_app_hardware_open_591374`).
  `lc3_hr_setup_encoder` is 0x59123A. The encoder caller is 0x59138A.
- No G2-specific changes to liblc3 were found.

### µLED panels: JBD4010 and Hongshi A6N-G over MSPI0
- **MSPI instance:** MSPI0, IRQ 20, priority 4. Completion is signalled through a binary semaphore at RAM 0x20074534. Interrupt mask 0x1A80; blocking timeout 1,000,000.
- **Panel option record (64 B):** selected by its type byte at +0x3C (0 = JBD4010 at ROM 0x70B024, 1 = A6N-G at ROM 0x70AFE4) and published at RAM 0x20074530.
  - Its 15 function slots cover term, chip ID, init, configure, power up/down, brightness, clear, current, offset, async/sync reflash, status check, mode, and SN.
- **JBD4010 opcodes:**
  - 0xA9 / 0xA3: open / close a register window.
  - 0xC0: display offset.
  - 0x46: 6-bit drive current.
  - 0x97: commit.
  - 0x71 / 0x72 / 0x73: modes.
  - 0x62: quad pixel write. Address word `((row<<10)&0x7FC00 | col&0x3FF)<<8 | 0xFF`; frame is 640×480 at 4 bpp.
  - 0x81: die ID, 12 bytes at 0x1FFF00.
  - 0x9F: chip ID. The status-check reply byte 0 must be 0x90.
- **A6N-G:**
  - Register access: write frames `{0x78|0x7A bank, reg, value}`; reads use instruction 0x79 / 0x7B, with 3 retries.
  - Chip ID: bank 0 register 0x06 must read 1.
  - Offset registers 0xEF / 0xF0, latched via 0xD9.
  - Health check: register 0xBE must read 0x84 (ASIC); register 0x62 must read 0x77 or 0x57 (panel); a mirror read of register 0xD8 must have bit 5 set.
  - Recovery: power off, 1 ms, power on, re-init.
  - The stock blocking `am_devices_hongshi_QSPI_PartialReflash` never transmits (it is a stub).
- **Display-driver manager queue:** 36-byte messages, depth 0x60.
  - IDs: 0 power up, 1 init (plus a 2 s timer), 2 clear, 3 reflash, 4 brightness, 5 power down, 6 timer recovery, 8 set mode.
- **Display thread:** 12-byte messages.
  - Types: 2 start/restart, 3 app data, 5 exit, 7 input event, 8 close all.
  - Input events map to LVGL event codes; the table is in `display_thread_handlers.c`.
- **GPU draw backend (Ambiq LVGL `5be8e0a`):**
  - Placement: fill 0x53DC38, border 0x53DF00, triangle 0x53E728, `nema_raster_line_aa`
    0x53EBBC, line 0x53ECFC, arc 0x53F09C, box_shadow 0x540036, mask_rect 0x5409F0.
  - Blending: ARGB8888 layers use NEMA_BL_SRC_OVER | NEMA_BLOP_SRC_PREMULT (0x04000501); other
    layers use NEMA_BL_SIMPLE.
  - `lv_draw_line_dsc_t` points are floats, so `LV_USE_FLOAT=1`.
  - Stock `lv_draw_arc`/`lv_draw_line` predate LVGL #8070.
- `lv_ambiq_gradient_create` / `dashline_create` come from an Ambiq `gpu_patch.c` that is not in
  the pinned ambiq-lvgl.
- `uled_mspi_setBrightness` is 0x4CA1EE; the existing name `display_driver_case4_apply` is misleading.

### Touch controller host driver and DFU (`driver/touch/drv_cy8c4046fni.c`, touch DFU service 0x55FD5A..0x5612xx)
- The part is a PSoC 4000T, CY8C4046FNI, on I2C bus 5 at 0x0C.
  - Attention input is GPIO27 (see the pin table).
  - Reset is logical channel 10: low, 10 ms, high, 50 ms.
- The transport table at RAM 0x20073E24 has four slots: cmd write, cmd read, raw write, raw read.
- Host command numbering is in [findings-touch-case §1.4](findings-touch-case.md). The table in
  `protocols.md` §9 and the older order in `docs/hardware/g2-glasses.md` §4 are stale.
  - Threshold write ACK is `07 00 17`.
  - The last-event report is 16 B and the diffs are 10 B.
- DFU uses the Infineon cy_dfu host protocol.
  - Frame: `01 cmd len16 payload(≤32) sum16 17`.
  - Command sequence:
    1. Enter 0x38 (product 0x01020304).
    2. Metadata 0x4C `{app 1, start 0x3300, len}`.
    3. SendData 0x37.
    4. ProgramData 0x49 `{addr, CRC-32C of the 128-B row}`.
    5. Verify 0x31.
    6. Exit 0x3B.
- `/firmware/touch.bin` is FWPK, record type 3. The CRC-32C table is at ROM 0x70F2A4.
- Stock quirk: the final DFU row is padded with heap bytes past the image, not with 0xFF.

### Sensor hub (`sensor_hub` thread, 0x4A6644..0x4A72xx) and eAT sensor handlers
- **Thread:** priority osPriorityHigh1 (0x29). Stack 0x2000 B at 0x20102C54. Thread-manager slot 5 (descriptor 0x20003664, 0x24-byte stride).
- **Queue:** `osMessageQueueNew(50, 8)`. Messages are `{u16 id, u32 value}`.
- **Route table** at RAM 0x20003688 (id → handler):
  - 1 SetMode, 2 register write, 3 calibration init, 4 IMU collection
  - 5 FuncOpen, 6 FuncClose, 7 empty hook, 8 ALS timer
- **Timer:** periodic `sensor_hub_timer`. It posts message 8, which runs `DRV_ALSTimerHandler`.
- **IMU interrupt:** data-ready is GPIO38. The callback is in the board pin table at ROM 0x686DB8 (12-byte rows). It timestamps the event and posts message 2, which calls `DRV_IMUReadData(tick)`.
- **Function-type arbitration:**
  - Types: 1 head-up, 2 compass, 3 dis, 4 ALS, 5 other.
  - IMU work mode priority: dis (1) > compass (2) > head-up/other (0). With no users left, the IMU is powered off.
- **Calibration:** NVDB record is 0x44 B: accel offset +4, gyro offset +0x10, 3×3 float matrix +0x1C.

### TDK ICM-45608 IMU glue (0x4A35B0..0x4A656E) and the linked TDK driver
- **Bus and IDs:** I2C bus 4 at 0x69, with one-byte register addressing. WHO_AM_I is 0x81.
- **Power and interrupt:** the power rail is codec GPIO channel 1: off, 100 ms, on, 5 ms. INT1 is active-high, pulsed, push-pull.
- **Magnetometer:** TDK ICT1531x behind the IMU's I2C master, at 0x1E. WHO_AM_I register reads 0x45. Scale is 0x1333/65536 µT per LSB.
- **Ranges and ODR:**
  - Accel ±4 g in LP mode. Gyro ±2000 dps in LN mode (LP when cell 0x2000454D is set).
  - ODR codes 6..11 correspond to periods of 1..40 ms.
  - The mode table is 5 × 16 B rows at RAM 0x20000DB0.
- **Head-up detection:** accel Z passes through a 2nd-order Butterworth low-pass at fs/100 (b = {9.446918e-4, 1.8893837e-3, 9.446918e-4}, a = {−1.9111970674, 0.9149758348}). Head-up when pitch > threshold and filtered Z < cos(threshold); head-down when pitch < threshold − 20°.
- **Compass:** heading = (yaw + 90) mod 360. Event 9 fires on a heading change larger than delta; event 0x10 reports calibration.
- **Mounting matrix:** comes from NVDB calibration, not code. It is cached as float (0x20000E38), Q14 (0x20000E00, also written to EDMP SRAM 0x1AC) and Q30 soft-iron (0x20000E14).
- **Upstream reuse:** about 90 functions at 0x504784..0x508B5A and 0x55D280..0x55D92C match `third-party/upstream/invensense-icm45608` @ b79ae575 (TDK 1.1.2). They cover `inv_imu_transport.c`, `inv_imu_driver*.c`, `inv_imu_edmp*.c` and `invn_mag.c`.
  - Stock variants: `inv_imu_remap_data` and `edmp_set_mounting_matrix` take a Q14 matrix; `invn_mag_init` caches WHO_AM_I; `b2s_*` comes from a different TDK drop.
  - The glue declares these functions as `inv_imu_*_<addr>` externs. Compiling the submodule for them is the next reuse step; they are not yet in `sources.json`.
- **IAR libm entry points:** cosf 0x50968C, sinf 0x509690, atan2f 0x50969C, asinf 0x509708, sqrtf 0x4397A8.
- **More TDK upstream files:**
  - `inv_imu_i2cm.c` is at 0x55D280..0x55D560 and `Ict1531x.c` at 0x55D588..0x55D7D8.
  - The stock `wait_us` variant 0x55D63C calls delay 0x491102.
  - The match makes the magnetometer an ICT1531x on driver evidence.

### Ambient light sensor: TI OPT3007 (0x4AD9B8..0x4AE9xx, register map 0x5135E0)
- I2C bus 2, address 0x45 (0x513748, 0x513780).
  - Chip-ID check: register 0x7E = 0x5449, register 0x7F = 0x3001.
  - Init writes M = 3 (continuous conversions) and CT = 0 (100 ms). RN is not written.
- The sensor rail is codec GPIO channel 9 (pad 0x86, shared with channel 6). Init waits 5 ms after power-on.
- Lux math:
  - raw = (R & 0xFFF) × 2^(R >> 12), in units of 0.01 lux.
  - The calibration word is at factory record 0x20003994+0x28. If it is 0, the value is raw/10. Otherwise it is raw × cal / 1,000,000.
  - The build-default calibration is 78953.
- Readings are discarded while IMU pitch is below −30°.
- Brightness curve at ROM 0x730E24 (threshold → %): {10,35} {200,50} {400,70} {1000,70} {1300,100} {∞,100}. The scaled target is clamped to 35..100 % with a Q10 scale.
- Extreme-dark mode forces 15 % brightness. It is entered when the filtered value is < 11 and at least 19 of the last 20 samples are < 3.
- State machine:
  - States: 1 start, 2 adjust, 3 polling. Periods are 1000 ms (start and polling) and 200 ms (adjust).
  - Ramp steps are +5 % / +2 % / −2 %.
  - Manual-brightness lock lasts 43201 s (12 h), although the log text says "2 hours".
  - The driver publishes brightness via sync message 0x10E rather than setting the display directly.

## BLE host to EM9305 controller

- **Transport:** HCI over IOM6, SPI mode 0 at 16 MHz. The config is in initialised data at 0x200001B4.
  The non-blocking transfer buffer is at 0x200703EC (0x40 words).
- **Controller pins:**
  - Outputs: GPIO149 = 1, GPIO93 (BLE_ENABLE) = 0, GPIO136 = 0.
  - Inputs: GPIO117 (radio IRQ, GPIO interrupt channel 0) and GPIO15.
- **Vendor HCI commands:**
  - 0xFC43 sets the public address; it is sent right after HCI_Reset.
  - 0xFFF2 writes 8 NVDS bytes.
  - 0xFCC4 sets the RF power level to +6 dBm.
- **Host changes:**
  - `HciGetLeSupFeat` (0x530D3C) clears bit 1 of the LE supported features.
  - The `hciCoreCb` layout at 0x20071478 matches Cordio r20.05c.
  - The ATT MTU floor is patched to 247 (`attsProcMtuReq` variant 0x56C6FC).
  - The Cordio files are AmbiqSuite R3.2.0 copies.
  - `HciLlPrivacySupported` is 0x530D54 (the TSV labels it `HciLeAdvExtSupported`).
- **Startup (`bleStackRegister`):**
  - DM client 3; the 6-entry CCC table is at ROM 0x7518C0.
  - It registers Even OTA, EUS, ESS, EFS and NUS.
  - The radio boots before a delayed start, which retries every 10 s.
- **Connection parameter profiles:**

  | Profile | Interval | Latency | Supervision timeout |
  |---|---|---|---|
  | Slow | 72–84 (90–105 ms) | 4 | 6 s |
  | iOS fast | 12–24 | 0 | 6 s |
  | Android fast | 12–24 | 0 | 6 s |

  - Phone type 4 means Android (byte at RAM 0x200737B0).
  - The link switches to the slow profile 60 s after connecting, unless terminal mode is on.
  - If the central rejects an update with 0x0C or 0x3B, the next try waits out a 30 s throttle.
    Any other failure retries after 10 s.
- **Ring link:** TX uses LE Coded PHY S8 and RX uses 1M PHY.
- **Arm status byte (RAM 0x20075043):**
  - Bits: 0 self OTA, 1 peer OTA, 2 self BLE, 3 peer BLE, 4 self ring, 5 peer ring, 6 ring MAC set.
  - It is synced in 8-B messages on channel 0x103: 1 OTA, 2 BLE status, 3 reply, 4 ring MAC set,
    5 ring query, 6 ring reply. Roles are R = 1, L = 2.

## NOR flash, XIP and storage

### MX25U25643G on MSPI1 (`driver\flash\drv_mx25u25643g.c`, object 0x46F4A4..0x471163)
- RDID 0x9F must return 0x2539C2.
- Reset is RSTEN 0x66 → 1 ms → RST 0x99 → 50 ms.
- RDCR 0x15 bit 5 means 4-byte address mode, which EN4B 0xB7 enters.
- Quad enable is SR bit 6, written with mask 0xC3, which also clears BP0..3.
- MSPI timing scan: 36 base settings × RxDQSDelay 0..31. The longest run of ID matches wins and is
  stored at RAM 0x20000820.
- `flash_mutex` is at 0x20072A88.
- Stock bug: a failed RST (0x99) logs "Write enable failed before sector erase".
- Resource reads use 0x6C (4-byte quad-output read). littlefs starts at NOR 0x01400000.
- XIP: firmware treats 0x80000000..0x81FFFFFF as the NOR window. The OTA storage type 1 check
  accepts addresses 0x80000000..0x82000000.

### littlefs port (`third_party/littlefs/port/littlefs_mx25u25643g_porting.c`)
- The geometry (`lfs_config` 0x6E83A4) is in [memory-map.md](memory-map.md).
- Block n maps to NOR 0x01400000 + n·0x1000.
- Init creates `/firmware`, `/ota`, `/user` and `/log`, and increments the `boot_count` file.

### KVDB "sysenv" (FlashDB 2.1.1, partition `kvdb`, `service_kvdb.c` 0x4D9530..0x4D9A97)
- FlashDB API: `fdb_kvdb_control` 0x545320, `fdb_kvdb_init` 0x5453FE, `fdb_kv_set_default` 0x5450A4,
  `fdb_kv_get_blob` 0x54454A, `fdb_kv_set_blob` 0x54503A.
- Default table: 12 nodes at RAM 0x2000372C.
- `kvMagic` must equal 0x5A000020. On a mismatch the database resets to defaults, but the
  onboarding byte survives. `kvbooCount` is incremented on every boot.
- Versioned records end in CRC-16/CCITT-FALSE (0x49ACD4). A record is migrated to its default when
  it is missing, or when it is corrupt and older than the current version.
- 11 migration callbacks live in a linker section at ROM 0x746D20..0x746D4C.
- Hardware-relevant keys:
  - `kvAlsScale` defaults to 0x400.
  - `kvRing` is 24 B: MAC + 14-char name, default "EVEN R1_FFFFFF".
  - `kvTerminalMode` is 4 B. Its stock default is `01 00 00 00`; the existing record at 0x20003808
    is zero-initialised.

### NVDB "factory" (partition `NVdb`, `service_nvdb.c` 0x5105F0..0x510991)
- `nvMagic` must equal 0x55550022.
  - Stock bug: on a mismatch the code resets to defaults and then reads `nvMagic` back instead of
    writing it.
- Records (default table at RAM 0x20003868, record-pointer table at 0x20003838):

  | Key | RAM | Size | Ver | Notes |
  |---|---|---|---|---|
  | nvAdvMagic | 0x200038D4 | 4 | 1 | |
  | nvBuzzer | 0x200038D8 | 12 | 2 | frequency, duty |
  | nvMAC | 0x200038E4 | 10 | 1 | |
  | nvProdMode | 0x200038F0 | 4 | 1 | the existing 2-B definition is too small |
  | nvSCald | 0x200038F4 | 92 | 1 | |
  | nvSCaldAG | 0x20003950 | 68 | 1 | accel[3], gyro[3], matrix[9] |
  | nvSysDt | 0x20003994 | 172 | 2 | CRC covers bytes 0..0x25 only |

- `nvSysDt` layout:

  | Offset | Field |
  |---|---|
  | +1 | PSN, 15 B |
  | +0x10 | BSN, 22 B |
  | +0x28 | ALS `lux_base` |
  | +0x2C / +0x2D | canvas x / y |
  | +0x2E | panel current |
  | — | three 40-B aging timestamps |
  | +0xA8 | counters |

- PSN format (14 chars): project[4], manufacturer 'L', colour, year letter ('A' = 2024), month
  letter, day[2], serial[4].
  - A ROM table at 0x6D3358 lists 40 legacy PSNs that change the display offset.
- OTP PSN copies: 8 slots × 16 B at 0x400C2340. A valid slot starts with "S2", and the last valid
  slot wins. The existing `am_hal_otp_*` names should be `am_hal_infoc_*`.
- Default BLE MAC: mac[0..3] = CRC-32 of the chip IDs, mac[4..5] = their CRC-16. mac[5] is then
  forced to the static-random form.
- On the right arm, a suspicious AG matrix is replaced in RAM by the ROM default at 0x759C60. The
  flash copy is left unchanged.

### OTA targets (`platform/protocols/ota_service/ota_service.c`)
- Command 0xC0 subcommands:
  - 0 START: fast connection, filesystem heal, session reset.
  - 1 INFO: requires the 0x80-B header.
  - 2: arm data.
  - 3 RESULT_CHECK: CRC-32C match replies {3,8}, mismatch {3,7}; {4,9} when an install is scheduled.
- Raw-data command 0xC1 acknowledges each chunk with {2,0}, or {2,6} on error.
- Header (0x80 B):

  | Offset | Field |
  |---|---|
  | +0 | encrypted |
  | +4 | start address |
  | +8 | length |
  | +0xC | CRC |
  | +0x20 | version |
  | +0x24 | data type |
  | +0x28 | storage type |
  | +0x2C | image id |
  | +0x30 | path (80 B) |

- Data types and targets:

  | Type | Image | Target |
  |---|---|---|
  | 0 | glasses firmware | `ota/s200_firmware_ota.bin` |
  | 1 | bootloader | `ota/s200_bootloader.bin` |
  | 2 | font | — |
  | 3 | touch | `firmware/touch.bin` |
  | 4 | codec | `firmware/codec.bin` |
  | 5 | EM9305 | `firmware/ble_em9305.bin` |
  | 6 | case | `firmware/box.bin` |
  | 7 | other | — |

- Storage types:
  - 0 = MRAM.
  - 1 = XIP NOR. Every write is read back and verified.
  - 3 = littlefs file. Each chunk is read back; on a mismatch the file is deleted.
- A successful glasses-firmware image sets the bootloader flag to 0x55555555 and disconnects after 3 s.
- The session object (RAM 0x20072730, 0x60 B) is shared by import and export.
- While OTA runs, `ble_msgtx` refuses every other sender.

## RTOS threads and queues

| Thread | Priority | Stack | Queue | Notes |
|---|---|---|---|---|
| `audio` | 47 | 8 KiB @0x20360E18 | 50 × 12 B | dispatch table 0x20003FBC |
| `input` | 0x2E | — | 30 × 12 B | thread-manager slot 4; touch, buzzer, in-case, terminal-mode messages |
| `sensor_hub` | 0x29 | 0x2000 @0x20102C54 | 50 × 8 B | slot 5 (descriptor 0x20003664, stride 0x24) |
| `ble_msgtx` | 0x30 | 16 KiB | 150 | kinds 1 TPL, 2 ESS, 4 EFS, 8 OTA |
| `ble_production` | 33 | 4 KiB | — | product-test frames over NUS |
| `uart_shell` | 24 | — | 0x800-B stream buffer | console UART channel 1 |
| FreeRTOS timer task | 54 | — | — | `xTimerCreateTimerTask` 0x47E674 |
| display | — | — | 12-B messages | driver-manager queue 0x60 × 36 B |
| AT | — | 32 KiB | — | the `at_core.c` comment saying 8 KiB is wrong |

- The kernel is the Ambiq FreeRTOS port with an STIMER tick. One WSF tick is 10 kernel ticks.
- The STIMER HAL at 0x48D570..0x48D704 is an older Ambiq variant without `AM_CRITICAL`.
- The compact-log ring descriptor is at 0x200004C8. Every 10000 ticks it syncs to files, at most
  9 × 4096 B at a time.
- Crash record at RAM 0x20075048, which survives reset:
  - Magic 'CRAS', text up to 0x1194 B.
  - On boot it is appended to `/log/hardfault.txt`, which is deleted once it exceeds 100 KiB.
  - CmBacktrace stages the text at 0x2005CE68.

## Product test, AT and CLI hardware commands

- Product-test frames are `5A A5 7F len payload sum8`. Payloads starting "AT" go to `AT_Handler`.
- About 66 command IDs are dispatched by `pt_protocol_dispatch` (0x56F50C..0x56F828).
  - The TSV `pt_cmd_XX_handler` names are wrong for 51 of 66 handlers.
  - `ghidra/pt-protocol/command-map.tsv` is off by one.
  - The case comments in `g2/src/apollo-main/app/a-55-pt-protocol/pt_protocol_procsr.c` hold the
    real map.
- Product-test command 0x47 drives GPIO134 high through WTS4 (0x4001044C).
- The MRAM program key 0x12344321 is used only by the AT memory-write command.
- CLI handlers are at 0x57E3E6..0x584702 and have no TSV rows.
  - `#Hardware version:` is printed via 0x57E6CC.
  - The panel `Chip id` comes from 0x592F9A, and the panel die ID is 6 × u16.
  - Product name "S200", software "2.2.6.10".
  - The codec version prints "0.0.0.0" on the arm without the codec.
- Filesystem CLI commands: ls, cat, rm, cd, mkdir, touch, pwd, mv, md5 and df, all on littlefs.
  The current directory is at RAM 0x200031B4. A memory command (0x57F550) walks the TLSF heap.
- Charging-case UART (product UART 2):
  - Receive ring: 5 × 1 KiB at 0x2005BA68.
  - A frame starting with 'T' is accepted as-is. Any other frame's last byte must equal
    (len + 0x7D + sum) & 0xFF.
- Buzzer (`driver\buzzer\drv_buzzer.c`, 0x5026BC..0x502D55):
  - TIMER7 PWM (function 4) on GPIO145, timer output 14.
  - The timer clock is 96 MHz / (4 << 2·clock_select). Init uses clock 0 (24 MHz) at 1 kHz, 30 % duty.
  - Tone scripts at ROM 0x6C1E2C hold 9 voices × 50 B; frequency = 1e6 / (0xFFFF − reload).
  - `DRV_BuzzerPlay` 0x502BF0 exists only as `audio_wear_child_502bf0`.

## Cross-cutting

- **Compressed log token.** `compress_log_output` (0x43CE9E) takes `level << 26 | nargs << 22`.
  Levels 1–4 are 0x04/0x08/0x0C/0x10 << 24.
- **elog assert hook.** The hook is at RAM 0x2007456C. When it is NULL the code logs "(%s) has
  assert failed" and spins.
- **SRAM init stream.** It is at 0x75D3F4, decoded by 0x43A11E. In each token, bits 1..0 hold the
  literal count n (n = 0 means next byte + 3) and n − 1 literals are copied. The high nibble holds
  the match length m (m = 15 means next byte + 15). The offset is the next byte plus
  `((token >> 2) & 3) << 8` (if that field is 3, the next byte is used instead). The match copies
  m + 2 bytes from `dst − offset`. A decoder is at `build/sensor-hub/sram.py` (ignored). Decoding the
  stream recovered the BQ27427 unseal key, the gauge descriptor table and the sensor-hub route table.
- **Misnamed cells and functions in `g2/src`.** For example, `audio_charge_sync_peer_record`
  (0x20074104) actually holds the *local* reading, and `hub_als_timer_callback` is the IMU GPIO38
  data-ready callback. The driver sources note each case.
- **CRCs.**
  - The file, OTA and touch-DFU CRC is CRC-32C, MSB-first (poly 0x1EDC6F41, table ROM 0x6983A8).
  - 0x4D34C4 is the standard reflected CRC-32. The GX8002 link uses zlib CRC-32.
  - KVDB/NVDB records use CRC-16/CCITT-FALSE (0x49ACD4).
- **IAR runtime quirks.**
  - `__aeabi_dcmpun` (0x43A19C) misses NaNs whose payload is only in the low word.
  - fminf/fmaxf choose −0/+0 as described in `iar_fminmax_p01.c`.
  - IAR scanf/strtod:
    - A literal mismatch returns max(0, nconv), and a NULL destination returns −35.
    - At most 36 significant digits are kept.

## Toolchain/ABI notes

These notes cover the stock main image, built with IAR EWARM. They apply to any C that is meant
to match it.

- **Float ABI:** stock uses the VFP calling convention, so float/double arguments and results
  travel in s0/d0.
  - Under the softfp FP profiles, each such function needs `__attribute__((pcs("aapcs-vfp")))`.
    Examples: `process_fuel_gauge` 0x51201C, `_Dtento`/`_Stodx`, `lv_line` `resolve_point_coord`
    0x5C9344.
  - A hard-float profile (`-mfpu=fpv5-d16 -mfloat-abi=hard`) would remove this need. INF: stock is
    fpv5-d16.
- **Enums:** IAR enums are one byte, so every unit that shares a struct with stock needs
  `-fshort-enums`. Affected examples: `am_hal_*` config records, `am_hal_uart` handle (0x11C), touch
  CAPSENSE, and LVGL.
- **Inlining:** IAR keeps `static` and `inline` helpers out of line. Upstream units therefore need
  `-fno-inline` (and `-ffunction-sections`) to emit them as separate functions.
  - Exceptions:
    - IAR ILINK inlines one-instruction functions at call sites.
    - Stock LVGL inlines some cross-file trivial accessors (INF: multi-file compilation).
  - INF: byte identity for these exceptions needs link-level handling.
- **`__LINE__`:** inside a multi-line macro invocation, IAR uses the line of the macro's last line.
  This affects assert and log line arguments.
- **LVGL assert:** stock `LV_ASSERT_HANDLER` is an endless store of 0 to address 0xFFFFFFFF (e.g.
  0x5C10FE..0x5C1106 in `lv_draw_arc`). It is recovered in
  `g2/config-recovered/lvgl/g2-config/lv_conf_recovered.h`.
  - Other fatal asserts use the same 10-B `*(0xFFFFFFFF) = 0; b .` pattern.
- **FreeRTOS port:** the IAR `portasm.s` (0x5FA058..0x5FA132) needs a GNU-syntax `.S` equivalent;
  the GCC `portasm.c` layout differs.

## Licence-blocked libraries identified

These libraries were identified in the stock images but not reconstructed. Their licences forbid
reverse engineering, so each needs a decision by the repository owner. Address ranges are
approximate.

| Library | Licence issue | Where (stock addresses) | Notes |
|---|---|---|---|
| Nordic `nrf_fuel_gauge` (closed binary, sdk-nrfxlib) | LICENSE clause 5 forbids reverse engineering | Main image: about 0x439CE0..0x43C260 (interleaved with IAR runtime leaves such as 0x43A11E), 0x55F74C..0x55FA20, 0x58EAB0/0x58EABC/0x58EAC4 | `ext_state_update` is byte-identical (modulo relocations) to sdk-nrfxlib `8f9ab9b0` cortex-m33 hard-float `libnrf_fuel_gauge.a`. `process` differs, so stock uses another release. INF: a binary-only link candidate. Internals include 0x43A698, 0x43BA6C, 0x43BB14, 0x43BC58, 0x43BC84, 0x43BE18, 0x43BFAC; ttf 0x55F9A0. 0x43C08E..0x43C0AE is unreferenced and has no row. |
| NemaGFX 1.4.12 / NemaVG 1.1.8 (Think Silicon, via Ambiq) | proprietary licence | Main image: the NemaVG stroker module 0x5640E4..0x56722A (tessellator 0x5657D8, stroke draw 0x567230, 0x5675A8, 0x5675B4); `nema_mat3x3_mul` 0x5619F2, 0x56395C, 0x5639E8, 0x564974, 0x5653A0; `nema_enable_gradient` 0x4B1588; `nema_vg_draw_path` 0x5202EC | INF: the "g2-freetype-engine-census" range 0x514xxx..0x52xxxx is likely NemaGFX/NemaVG, not FreeType. |
| EM9305 SDK v4.2 / Packetcraft controller (EM Microelectronic) | proprietary SDK archives | EM9305 image: 185 rows match blocked SDK archives, and 19 more are probable SDK | ~71 `packetcraft_modern_controller` rows count as covered only through address mentions. |
| Cypress/Infineon CAPSENSE 6.10 (`247a9a0`) and Em_EEPROM 2.60 | Cypress EULA clause (iii) forbids reverse engineering | Touch image: see [findings-touch-case.md](findings-touch-case.md) §1 (e.g. CAPSENSE 0x5D90, 0x5FBA; Em_EEPROM 32 functions / 2,864 B) | About 75 existing reconstructions. |

Some existing `g2/src` files already contain reconstructions of these libraries. They are
**pending a decision by the repository owner** and have not been removed:

- NemaGFX/NemaVG:
  - `g2/src/apollo-main/graphics/nema-vg/`.
  - In `graphics/ambiq-buffer-handlers/`: `vector_path_state.c`, `stencil.c`, `nema_trigonometry.c`
    and `matrix_rotate.c`.
  - Two definitions of 0x4B1588: `display_driver_gpu_mode_mask_4b1588` and
    `display_driver_nema_cache_4b1588`.
  - `audio_uart_ambiq_vector_shape_draw_5202ec`.
- EM9305/Packetcraft:
  - In `g2/src/em9305/qpc-scheduler/controller_init.c`: `opencfw_em9305_controller_initialize_stack`,
    the link-command and LL-record bodies.
  - `initializer_lowers/init_packet_switch_known.c`.
  - The PML/ProtTimer/SLEEP_MANAGER/WSF/lctr code listed in the em01 report.
- CAPSENSE/Em_EEPROM: the reconstructions under `g2/src/touch/`.
- `nrf_fuel_gauge`: no reconstruction was made.

Other licence notes:

- The Ambiq copies of Cordio `wsf_os.c`/`wsf_buf.c` carry Wicentric/ARM proprietary headers.
- The case image's Arm C library (armlib) is proprietary and has only hand-written equivalents.
- `asin` 0x43C260 would need licensed IAR DLIB source.

## Open items left by this pass

- **Upstream TDK driver.** Add `third-party/upstream/invensense-icm45608` sources as `upstream` units,
  then map the IMU glue's `inv_imu_*_<addr>` externs onto them, after reconciling the stock variants
  listed above.
- **IOM HAL interrupt functions.** 0x55C174, 0x55C498, 0x55C4D0, 0x55C518 and 0x55C558 have no C
  yet. The island's existing functions should be renamed from `audio_ble_*` to their `am_hal_iom_*`
  roles.
- **Same stock function defined twice under different names** (pre-existing display units):
  - 0x5926EE: `display_driver_uled_command_5926ee` and `display_driver_uled_type0_aux_reg_write_5926ee`.
  - 0x59C876: `display_driver_uled_device_check_59c876` and `display_driver_uled_device_reconfigure_59c876`.
  - 0x59C980: `display_driver_uled_packet_begin_59c980` and `display_driver_uled_serial_mode_59c980`.
  - 0x59CA2C: `display_driver_uled_packet_end_59ca2c` and `display_driver_uled_quad_mode_59ca2c`.
  - 0x449376: `audio_delay` and `g2_norflash_scheduler_delay_449376`.
  - 0x464D1C: `audio_ble_send_status_message` and `audio_uart_input_event_send_464d1c`.
- **Existing copies that keep a non-stock name and so cannot anchor.** Charger: `CHG_InitBatterySync`,
  `CHG_GetSoc`, `CHG_GetIsCharging`, `CB_CHG_*`, `CB_RING_BAT_Init`, `SVC_RingBattery_RequestFromPeer`.
  The uLED manager's `display_driver_case*` functions. The GX8002 transport's `audio_transaction_*`
  and `audio_packet_pack`. The IMU's 0x4A4E8C, 0x4A4EC0 and 0x4A52A2.
- **Two declarations for 0x20073B30.** `audio_charge_sync_record` and `audio_charger_state` both
  name it.
- **Compiler choice.** clang `-mfpu=fpv5-sp-d16` softfp lowers the stock double-precision VFP code
  (`vcvt.f64`, `vmul.f64`) to `__aeabi_d*` calls. Stock uses fpv5-d16 with the hard-float calling
  convention.

## Tooling

REA was built from the pinned checkout (`third-party/tools/rea`, 7aa4d768) into `build/rea-tool`
(`npm ci && npm run build`). It analyses an executable ELF wrapper of the authenticated main image.
That wrapper converts back to the original bytes:

```sh
arm-none-eabi-objcopy -I binary -O elf32-littlearm -B arm \
  --rename-section .data=.text,contents,alloc,load,code,readonly ota_s200_firmware_ota.bin blob.o
# s.ld: ENTRY(_start) _start = 0x438000; SECTIONS { . = 0x437fe0; .text : { blob.o(.text) } }
arm-none-eabi-ld -T s.ld -nmagic -o apollo-main-2.2.6.10.elf blob.o
```

To run it, set `JAVA_HOME` to a JDK 21, set `GHIDRA_INSTALL_DIR` to a Ghidra 12.1.4 install, and
optionally raise `REA_GHIDRA_STARTUP_TIMEOUT_MS`:

```sh
node build/rea-tool/scripts/rea.mjs decompile <elf> 0x<addr> --provider ghidra --snapshot <file> --json
```

Each query re-imports the image, which takes about 70 s. Compared with the corpus export, REA's
pseudocode resolves literal-pool values and strings to their real addresses.
