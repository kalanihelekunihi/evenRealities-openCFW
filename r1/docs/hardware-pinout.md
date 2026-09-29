# R1 hardware pin, bus and peripheral map (stock 2.2.6.0009)

MCU: Nordic nRF52840 QIAA, Cortex-M4F at 64 MHz, 1 MiB flash, 256 KiB RAM
(`r1/platform/nrf52840/zephyr/boards/openr1/openr1_nrf52840/openr1_nrf52840.dts:4`;
`r1/docs/correlation/NORDIC-SDK-CORRELATION.md:587-589`). The board/module identity string is
`603MV1.9.3` (Bravechip BCL603M family). The product code is B210.

Pins are written `Px.yy`; the absolute GPIO number is `32*x + yy`. Most facts come from the
scatter-initialized board registries in the application image (Proven). The openR1 Zephyr
dts/pinctrl (`config-recovered/openr1_nrf52840*.dts*`) encodes the same map and is cited as a
compact cross-check. Tags: **Proven**, **Strong**, **Inferred**, **Unverified**.

## 1. Two-wire buses (6-entry board registry)

Registry wrappers are at `0x00054F90`/`0x00054FC4` (hardware) and `0x00056508..0x00056550`
(software) (`r1/docs/correlation/BUS-REGISTRATION-CORRELATION.md:10-35`;
`r1/docs/reference/r1-capability-matrix.csv:102` (R1-101)).

| Bus | Kind | SCL | SDA | Speed / delay | Record | Devices | Tag |
|---|---|---|---|---|---|---|---|
| `i2c_0` | TWIM0 (`0x40003000`) | P0.12 | P0.01 | 400 kHz (`0x06680000`), IRQ prio 2, no hold after uninit | `0x20006FF4` (xfer state `0x20006FE8`) | Azoteq IQS7211E touch, 7-bit `0x56` | Proven |
| `i2c_1` | TWIM1 (`0x40004000`) | P0.11 | P0.14 | 400 kHz | `0x20007060` (xfer state `0x20007054`) | accelerometer at 7-bit `0x18` (LIS2DW12 / BMA456W); QMA6100 fallback at `0x12`/`0x13` | Proven |
| `i2c_2` | software bit-bang | P1.13 | P0.28 | delay arg 1; u8 register | `0x20007400` | GXT310 x2: `GXT310X0` 8-bit `0x90`, `GXT310X2` 8-bit `0x94` | Proven |
| `i2c_3` | software | P0.11 | P0.12 | delay arg 5; u8 register | `0x20007470` | none (dormant; registry string only). Shares pins with TWIM0 SCL and TWIM1 SCL | Proven |
| `i2c_4` | software | P1.09 | P0.31 | delay arg 1; u16 register/count | `0x200074E0` | Goodix GH3x2x optical (register-16 protocol) | Proven |
| `i2c_5` | software | see note | see note | delay callback `0x00054AF1` is a no-op; u16 register | `0x20007550` | ST25DVxxKC NFC (8-bit `0xA6` user memory / `0xAE` system registers) plus the YHM2710 STACMD wrapper | Proven (pins); SCL/SDA order conflicting |

Sources:
- `i2c_0`: `r1/docs/boundaries/IQS7211E-PROVIDER-BOUNDARY.md:101-122`.
- `i2c_1`: `r1/docs/correlation/MOTION-PROVIDER-CORRELATION.md:136-139`; `r1/docs/README.md:709-712`.
- `i2c_2` to `i2c_5`: `r1/docs/boundaries/SOFTWARE-TWI-PROVIDER-BOUNDARY.md:44-49`; `r1/docs/boundaries/NAMED-PERIPHERAL-BOUNDARIES.md:13`.
- `i2c_5`: `r1/docs/correlation/ST25DVXXKC-CORRELATION.md:40-42`; `r1/docs/correlation/I2C5-DELAY-CALLBACK-CORRELATION.md`.

`i2c_5` pin-order conflict (Unverified which is right):
- `r1-capability-matrix.csv:87` (R1-086) says "clock GPIO43/P1.11 and data GPIO46/P1.14".
  `YHM2710-I2C5-RESOURCE-BOUNDARY.md:65`, `ST25DVXXKC-CORRELATION.md:168` and
  `NORDIC-SDK-CORRELATION.md:844` agree with it.
- The software-TWI boundary table (`SOFTWARE-TWI-PROVIDER-BOUNDARY.md:49`, "SDA/SCL" column
  `P1.11 / P1.14`) and `r1/reconstructed/software_twi/software_twi.c:125` give SCL P1.14 /
  SDA P1.11.
- Resolve this by decoding the record at `0x20007550` (+0x04 = SCL, +0x08 = SDA per
  `SOFTWARE-TWI-REDUCTION-CORRELATION.md:58`) in the decompressed RW image.

Software-TWI engine (Proven; `SOFTWARE-TWI-PROVIDER-BOUNDARY.md:21-83`;
`r1/docs/correlation/SOFTWARE-TWI-REDUCTION-CORRELATION.md:55-100`):
- It is a per-bus callback-vtable engine with 10 roles per bus. The bodies are at
  `0x00055330..0x00056274`, and read-byte/start/stop/ACK/write-byte are byte-identical across
  buses.
- Read transaction: start, address, register, repeated start, address|1, N bytes, stop.
- Write transaction: address, 16-bit register MSB-first, one data byte.
- Status codes 0..12 are shared with the device registry.
- There is no clock stretching. A NACK aborts with 11 and sends no STOP.
- The `i2c_4` open additionally calls `nrf_gpio_cfg(pin,1,1,0,0,0)` for SCL, then SDA.

## 2. GPIO registry

**Inputs**: seven records of 44 bytes at `0x200070C0`, all no-pull, low-accuracy PORT events.
Dispatcher `0x0006ED94` scans them in the order below and continues after a match, because P1.01
appears twice (`r1/docs/correlation/GPIO-INPUT-IRQ-DISPATCH-CORRELATION.md:9-20`;
`r1-capability-matrix.csv:103` (R1-102)). Tag: Proven.

| # | Name | Pin | Edge | Device |
|---:|---|---|---|---|
| 1 | `acc_int_1` | P0.15 | rising | accelerometer INT1 |
| 2 | `ppg_int` | P0.21 | falling | Goodix GH3x2x INT |
| 3 | `touch_rdy_in` | P0.17 | falling (word `0x00000200`) | IQS7211E RDY/MCLR (active-low) |
| 4 | `mcu_reset_irq` | P0.18 | falling | reset pin alias (PSELRESET = P0.18); registry string only |
| 5 | `pmic_irq` | P1.01 | falling | YHM2710; registry string only |
| 6 | `nfc_gpo_irq` | P0.03 | rising | ST25DV GPO |
| 7 | `device_stacmd_irq` | P1.01 | falling | YHM2710 STACMD line |

**Outputs**: five 56-byte task-capable toggle outputs (`r1-capability-matrix.csv:103`). Tag: Proven.

| Name | Pin | Initial level | Function |
|---|---|---|---|
| `ppg_led_en` | P0.10 | low | Goodix emitter / LED enable |
| `touch_ldo_en` | P0.30 | low | IQS7211E LDO |
| `ppg_reset_en` | P1.04 | low | Goodix reset |
| `ship_mode_en` | P0.09 | low | destructive PMIC ship mode |
| `touch_rdy_out` | P0.17 | high | IQS7211E RDY/MCLR drive (bidirectional with input 3) |

**Other fixed pins**

| Pin | Function | Tag | Source |
|---|---|---|---|
| P1.01 | YHM2710 single-wire STACMD (`device_stacmd`, ops `0x20007614`) | Proven | `r1/docs/correlation/YHM2710-REDUCTION-CORRELATION.md:63`; `r1/docs/PROVENANCE.md:77` |
| P1.10 | NFC dock / ST25 board enable. `PIN_CNF` word `0x0000030F` (output, input disconnected, …). Activation: low, 10 ticks, high, 10 ticks, then acquire `i2c_5` (`0x000504D8`) | Proven | `r1/docs/boundaries/YHM2710-I2C5-RESOURCE-BOUNDARY.md:24,28,105` |
| P0.18 | nRESET (`CONFIG_GPIO_AS_PINRESET` → UICR PSELRESET) | Proven | `r1/docs/correlation/NORDIC-SYSTEM-INIT-CORRELATION.md:49-53` |
| NFC pins P0.09/P0.10 | used as GPIO (`CONFIG_NFCT_PINS_AS_GPIOS`); they carry ship mode and the PPG emitter | Proven (flag) / Inferred (link) | same |

## 3. SAADC (3 channels)

Records are three 40-byte entries at `0x20006EF8`. Configuration: 12-bit, no oversampling,
normal power, IRQ priority 6, single-ended, internal 0.6 V reference, burst off
(`r1/docs/correlation/ANALOG-BATTERY-CORRELATION.md:27-38`; `r1-capability-matrix.csv:83` (R1-082)).
Tag: Proven.

| Name | Ch | Input | Pin | Gain | t_acq | CONFIG | Use |
|---|---:|---|---|---|---|---|---|
| `vbat_adc` | 0 | AIN5 (PSELP 6) | P0.29 | 1/2 | 40 µs | `0x00050400` | battery voltage |
| `vpmic_isns_adc` | 1 | AIN3 (PSELP 4) | P0.05 | 1/2 | 40 µs | `0x00050400` | PMIC current sense |
| `vnfc_rect_adc` | 2 | AIN2 (PSELP 3) | P0.04 | 1/6 | 10 µs | `0x00020000` | NFC rectifier |

Conversions (Proven; `r1-capability-matrix.csv:84` (R1-083)):
- Battery `0x91184`: take 5 samples, drop the 2 lowest, average 3, then compute
  `avg*0xD5154/0x79D38`.
- While charging, runtime `0x31FCC` adds the persisted correction (−299..299) and divides by
  Float32 `0x3F86C8B4`.
- NFC `0x50D00`: `(((avg*3600+2048)&0x0FFFFFFF)>>12)*331/51`.

## 4. Peripheral details

### IQS7211E touch (`i2c_0`)

Source: `IQS7211E-PROVIDER-BOUNDARY.md:84-140`; `r1/docs/correlation/IQS7211E-ATI-AUDIT-CORRELATION.md:24`. Tag: Proven.

- Registers are little-endian words; the audit register is `0xE3`.
- Reset/ATI acknowledgement bytes: `33 A0 00 6C 47 00 00`.
- Power-up sequence:
  1. delay 1, raise P0.30, delay 10;
  2. close RDY, drive P0.17 high then low, delay 130;
  3. drive P0.17 high, delay 10, return to default, delay 20.
- Slider configuration is at `0x200067C4`: long-press 1000, bounds 10..180, span 200, pressure
  reference 240.0, calibration scale 213.333
  (`r1/docs/correlation/TOUCH-SLIDER-CORRELATION.md:51-62`).

### Accelerometers (`i2c_1`)

Source: `MOTION-PROVIDER-CORRELATION.md:53-54,136-153`; `r1/docs/README.md:709-713`. Tag: Proven.

- Probe order: LIS2DW12 (WHO_AM_I reg `0x0F` = `0x44`), then BMA456W, then QMA6100 (chip ID
  `0xFA`, or `0x9x` for the P variant).
- BMA456W: ODR 25/50/100/200 Hz → 6/7/8/9, ±8 g, 450 µs settle.
- LIS2DW12: ODR → 3/4/5/6 (150 Hz maps to 200), reset then 2 ms polling, auto-increment + BDU.
- QMA6100: 25 Hz setup.
- FIFO timestamp is u32 at 1024 Hz.

### Goodix GH3x2x (`i2c_4`)

INT P0.21, emitter P0.10, reset P1.04. Shares YHM power-lease client bit 1. Profiles 2000/4000
are the factory selections (`r1/docs/correlation/FACTORY-F2-HIGH-RISK-CORRELATION.md:13`). Tag: Proven.

### GXT310 x2 (`i2c_2`)

Addresses `0x90`/`0x94` (8-bit). Register 0 holds a signed big-endian value; LSB `0.0078125` °C
per the GXCAS demo. Calibration is 6 bytes at `nv_r1+0x3E`. Pair enable is at `0x00050F9C`
(`NAMED-PERIPHERAL-BOUNDARIES.md:13-31,63-65`; `r1/README.md:223-227`). Tag: Proven (addresses);
Strong (scale).

### ST25DVxxKC NFC (`i2c_5`)

Source: `ST25DVXXKC-CORRELATION.md:40-48`; `r1/docs/correlation/NFC-DOCK-POLICY-CORRELATION.md:29-46`. Tag: Proven.

- GPO on P0.03 (rising). Enable pin P1.10.
- Mailbox at `0x2008` (max 256 bytes); dynamic IT status register at `0x2005`; ST timeout 320.
- The dock protocol uses a 23-byte packet. A mailbox control byte of `0x81` permits a reply.
- Delay selection is 60 s or 4 s. The heartbeat counter resets at 61.

### YHM2710 PMIC / charger (P1.01 STACMD)

Source: `YHM2710-REDUCTION-CORRELATION.md:55-76`; `r1-capability-matrix.csv:82,87-89`. Tag: Proven.

Wire protocol on P1.01:
- A command is accepted only if bit 6 is set. Header = `(cmd & 0xF0) + reg`.
- 7 header bits, then a read (1) or write (0) selector.
- 8 data bits MSB-first with XOR parity. A read drives parity after every byte except the last.
- Bit timing: 52 µs and 13 µs pulses (one and zero use the same edges). Recovery/idle uses a
  209 µs delay (the `nrf_delay_us` veneer, ×64 cycles).
- Each edge is bounded to 1000 samples. Retries are 1..9.

Registers and actions:
- Chip ID register 8 = `0xA0`.
- Init writes `(2,01) (0,6A) (1,4C) (2,A0) (3,02)`.
- Register 6 high nibble: A/B/C = charging, D = charged.
- Register 1 bit `0x02` is `sys_track`. Register 1 ladder scale is 20.080322 with multipliers
  `{0.5,0.2,0.7,0.9,1.0,1.5,2.0,3.0}`.
- Power lease is a 3-bit client mask (bit 0 battery, bit 1 optical, bit 2 touch). The first
  acquire writes register 2 = `0xA8`; the final release writes `0x28`; the high-temperature path
  writes `0xF8`.
- NFC readiness: register 5 bits 7..5 = `101`, register 6 high nibble = C, register 7 bit 7
  clear; repair sets register 3 bit `0x40`.

## 5. Clocks, timers, watchdog, RTOS

| Item | Stock value | Tag | Source |
|---|---|---|---|
| HFCLK / CPU | 64 MHz (`SystemCoreClockUpdate`; delay 64 cycles/µs) | Proven | `NORDIC-SYSTEM-INIT-CORRELATION.md:42`; `NORDIC-SDK-CORRELATION.md:587-589` |
| LFCLK (app) | internal RC. `nrfx_clock_enable` writes LF RC to `LFCLKSRC`, IRQ priority 6. SoftDevice LF config `00 10 02 01`: RC, 4 s checks, 8 s forced calibration, 500 ppm; extended drift calibration enabled | Proven | `NORDIC-SDK-CORRELATION.md:561-583`; `r1-capability-matrix.csv:201` |
| LFCLK (bootloader) | same bytes at `0x000FDC68` | Proven | `r1/docs/closures/AUGUST-18-R1-B56EE2-HARDWARE-VALIDATION.md:30-35` |
| S140 app IRQ mask | `0xBDFF06FC` | Proven | `NORDIC-SDK-CORRELATION.md:568` |
| RTC2 (`0x40024000`) | `sys rtc` device, prescaler 4095 → 8 Hz, epoch + int16 UTC offset (minutes x 60), 256-entry named alarm table | Proven | `NORDIC-SDK-CORRELATION.md:683`; `r1/docs/correlation/CLOCK-PRODUCTION-CORRELATION.md:12-16`; `r1/docs/boundaries/RTC-DEVICE-PROVIDER-BOUNDARY.md:46` |
| RTC1 | FreeRTOS tick 1024 Hz (Nordic nRF52 RTC port, tickless idle) | Strong | `NORDIC-SDK-CORRELATION.md:745-813`; `r1/docs/README.md:695-698` |
| TIMER2 (`0x4000A000`), TIMER4 (`0x4001B000`) | nrfx timer instances in use (4 and 6 CC channels) | Proven | `NORDIC-SDK-CORRELATION.md:684-685` |
| SPIM2 (`0x40023000`) | enabled, non-extended; purpose unassigned | Proven | `NORDIC-SDK-CORRELATION.md:662-673` |
| PDM | IRQ handler linked (vector `0x000270B4` → `0x000309DC`); use not established | Proven (linked) | `NORDIC-SDK-CORRELATION.md:921-926` |
| NFCT | `nrfx_nfct` IRQ + helpers linked | Proven | `NORDIC-SDK-CORRELATION.md:539-550` |
| GPIOTE | 8 high-accuracy channels plus low-power PORT events (channel IDs >7) | Proven | `NORDIC-SDK-CORRELATION.md:700-724` |
| WDT (`0x40010000`) | behaviour 1 (run in sleep, pause in debug), reload 10,000 ms, IRQ priority 6, 1 channel, no-op timeout handler; record `0x20007630` | Proven | `r1/docs/correlation/WATCHDOG-DEVICE-CORRELATION.md:30-43` |
| Bootloader WDT | feed reload − 3200 ticks, floor 150 | Proven | `r1/research/bootloader-reconstruction/README.md:113` |
| Sensor-stream framework | 1024 Hz base, timer `1024/rate` | Proven | `r1/docs/PROVENANCE.md:97` |
| DC/DC REG1 | enabled at BLE init; switchable via `systemSettings` (`sd_power_dcdc_mode_set`) | Proven | `r1-capability-matrix.csv:197` |

## 6. openR1-only choices to ignore

- Zephyr dts `touch-rdy-gpios` flag `GPIO_ACTIVE_HIGH` and the `nfc-bus = <&i2c1>` binding. Stock
  RDY is active-low, and NFC is on software `i2c_5`, not TWIM1
  (`openr1_nrf52840.dts:31-36`).
- Zephyr RTC0/RTC1 ownership notes (`openr1_nrf52840.dts:55-61`). Stock RTC0 belongs to S140
  and RTC1 to the FreeRTOS tick (Inferred).
- openR1 `sdk_config.h` has `NRFX_TIMER` disabled and PDM/NFCT absent, but stock links TIMER2/4,
  PDM and NFCT.
