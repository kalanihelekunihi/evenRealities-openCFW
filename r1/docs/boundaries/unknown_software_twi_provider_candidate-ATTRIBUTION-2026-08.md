# Attribution re-examination — unknown_software_twi_provider_candidate (2026-08)

## Family

40 functions, `0x00055330..<0x00056274` (3,524 bytes incl. gaps), four compiler-instantiated
GPIO bit-bang two-wire engines (`i2c_2`..`i2c_5`), ten roles each: open, read_adapter,
read_byte, read_transaction, start, stop, ack (wait-ACK), write_adapter, write_byte,
write_transaction. Ledger disposition: `investigate_before_implementing`.

## Methods

- The engine region `0x000552DC..0x000562DF` is absent from the Ghidra inventory
  (`decompiler-output.c`, `disassembly.s`, `functions.csv`, `call-graph.csv`); it survives
  only in the byte-rebuild corpus. All bodies were therefore disassembled directly from
  `r1/research/decompilation/rebuild/rebuilt-application.bin` (load base 0x27000, capstone
  5.0.7, Thumb-2).
- Full-image pointer scan for all 40 entry addresses: aligned and unaligned words, odd and
  even values, and `movw`/`movt` immediate-pair encodings — zero references of any form.
- String/corpus mining of the rebuilt image for platform fingerprints.
- Upstream comparison against RT-Thread v4.1.0 `components/drivers/i2c/i2c-bit-ops.c`
  (fetched from github.com/RT-Thread/rt-thread, tag v4.1.0, Apache-2.0).

## Recovered structure (instruction-level)

Per-bus engine state (record base + 8): `delay_ctx@0x00, scl@0x04, sda@0x08,
drive_low(pin)@0x0C, release_high(pin)@0x10, set_output(pin)@0x14, set_input(pin,pull)@0x18,
pull@0x1C, udelay(ctx)@0x20, read_pin(pin)@0x24`; a seventh op at engine +0x28 (record +0x30)
is the pin-release (`nrf_gpio_cfg_default`) path used by the admitted close wrappers.
Open-flag byte at record+4. Registry sub-record at record+0x34: `{name, ops@record+0x4c, ...}`.

- open (`0x55330`): idempotent via open-flag; `set_output(SCL/SDA)` then `release_high(SCL/SDA)`.
  The divergent i2c_4 open (`0x55390`, 78B) additionally calls the six-argument Nordic
  `nrf_gpio_cfg` wrapper twice — in-house HAL special-casing inside the engine.
- start (`0x55A18`): set_output SCL,SDA; release SCL,SDA; udelay; drive SDA low; udelay;
  drive SCL low; udelay (tail).
- stop (`0x55B10`): drive SDA low; udelay; release SCL; udelay; release SDA (tail).
- ack/wait-ACK (`0x55BC0`): set_input(SDA,pull); udelay; release SCL; udelay; read SDA —
  returns 1 on NACK (error polarity); then drive SCL low; release SDA... (72B).
- read_byte (`0x55548`): MSB-first, `byte=(byte<<1)|sda` per bit with SCL release/sample/drive;
  trailing ACK (drive SDA low) or NACK (leave released) pulse selected by flag argument.
- write_byte (`0x55FA4`): MSB-first; per bit `drive_low/release_high(SDA)`; udelay;
  release SCL; udelay; drive SCL low; releases SDA after bit 7 (in-loop ACK-window prep).
- read_transaction (`0x557F8`): start / addr(W) / reg / repeated-start / addr(R) / N-1 bytes
  with ACK + last byte NACK / stop; any NACK → status 11 (0x0B).
- write_transaction: i2c_2..4 single-byte (`addr, reg16 MSB-first, 1 byte`); i2c_5
  (`0x56202`, 114B) is the multi-byte variant (N-byte loop, ST25DV-style).
- Adapters: read returns 4 (null request) / 10 (not open) / 12 (transaction NACK); write
  returns 4 / 8 / 11. With the registry's missing-operation codes {1,2,3,5,6,7,9} these form
  one gap-free positive status enum 0..12 — single-authorship interlock with the
  generic-device-registry family. i2c_5's read adapter merges null-request and not-open into
  a single return-4.

## Cross-instance folding

The census's "i2c_2 write_transaction" at `0x560DC` calls the *i2c_5* primitives
(`0x55AD2/0x5608E/0x55C98/0x55B94`); i2c_5's write_adapter tail-calls `0x560DC` for the
single-byte case. The four byte-identical copies of start/stop/ack/read_byte/write_byte are
linker artifacts of one generic body; per-bus attribution of individual copies is nominal.

## Flash-reachability finding

No reference to any of the 40 entry points exists anywhere in flash in any encoding
(verified exhaustively). The runtime vtable installer therefore cannot use literal pools,
`.data` templates, or `movw/movt` construction; it must sit in a Ghidra corpus gap using
PC-relative addressing, or reach records indirectly via the registry (`find(name)-0x34`).
Refined next step: disassemble corpus gaps `0x52B18..0x5380C`, `0x56314..0x563C4`, and
`0x5655E..0x566AC` for multi-word function-pointer stores into indirectly based records.
(Init table at `0xC454C..0xC4567` = {0x563C5, i2c_2..i2c_5 wrappers, 0x565F5, 0x56695}; the
last two are further registry wrappers for records at `0x200075C0`/`0x20007630`.)

## Platform fingerprint (who wrote it)

Embedded strings: `product/B210/app/_build/B210_Application`;
`..\..\..\platform\ble\app_ble_init.c`; `..\..\..\platform\services\eAT\at_system.c`;
`..\..\..\platform\threads\thread_manager.c`;
`..\..\..\third_party\DB\FlashDB\src\fdb_tsdb.c`; `[RING]` log namespace;
`g_thread_ble.h_message_queue`. Genuine third-party components in the same image keep their
own namespaces (`gh3x2x-v2.23_7ecd2a`, `pGGh3x2x_Virtual_Reg_v3.4`, GoMore, `[FlashDB]`,
nrfx, SoftDevice, CMSIS-FreeRTOS). The TWI engine carries no third-party namespace and lives
in the Windows-built `platform\` middleware tree for product B210 (see the sibling-family
report `unknown_shared_quantized_neural_runtime_candidate-ATTRIBUTION-2026-08.md` for the
Wuxi Bravechip "ChipletRing" / BCL603M platform identification, including the byte-exact
GATT base-UUID match to Bravechip's public APPSDK).

## Hypotheses tested

### H1 RT-Thread `i2c-bit-ops` — NO MATCH (any version; struct stable since 2012)
Tested against fetched upstream v4.1.0 source (Apache-2.0).
- Ops model differs fundamentally: RT-Thread `rt_i2c_bit_ops` =
  `{data, set_sda(data,state), set_scl(data,state), get_sda, get_scl, udelay(us), delay_us,
  timeout}` (level-set, single data ctx); R1 = direction-based open-drain six-op vtable
  `{drive_low, release_high, set_output, set_input(pin,pull), udelay(ctx), read_pin}` with
  per-pin handles.
- RT-Thread `i2c_writeb`: `SCL_L → set data → delay → SCL_H` with clock-stretch timeout wait;
  R1 write_byte: `set data → delay → release SCL → delay → drive SCL low`; no `get_scl` op
  exists — no clock stretching anywhere in the engine.
- RT-Thread `i2c_waitack` returns ack=true on SDA-low; R1 ack returns 1 on NACK (inverted
  polarity), feeding positive status 11.
- RT-Thread returns negative `rt_err_t`; R1 returns the positive 0..12 enum.
- Confirms and substantiates the boundary doc's prior rejection.

### H2 Nordic `twi_sw_master` — NO MATCH
Compile-time single bus, direct `nrf_gpio` macros at the call site, no runtime vtable, no
per-bus state records, boolean returns. The R1 engine's defining feature (runtime-installed
per-bus vtable, four instances) has no counterpart. (Consistent with prior rejection.)

### H3 Linux `i2c-gpio`/`i2c-algo-bit`, Zephyr `i2c_bitbang` — NO MATCH
Wrong ecosystem (Linux kernel / Zephyr driver frameworks absent); both use level-set ops and
an adapter/algo framework, not a runtime record vtable with positive status enums.

### H4 Sensor-vendor SDKs (Goodix GH3x2x democode, ST ST25DV, YHM2710, GXT310) — NO MATCH
One byte-identical engine drives all four buses across four different vendors' devices; no
single vendor SDK scopes that. Vendored libraries in the image carry their own namespaces;
none matches.

### H5 Generic Chinese-platform SDK (Bluetrum/Jieli/Realtek/Goodix GR55xx/GoMore) — NO MATCH
Build-path strings place the middleware in the `product/B210` tree
(`platform\...`, Windows path separators). Prior cross-firmware scan of 59 sibling blobs and
code-host searches for the rare device names (`device_stacmd`, `mcu_reset_irq`,
`touch_rdy_out`, `sys rtc`) were all negative; this re-examination adds negative results for
`g_thread_ble` / `thread_ble.h_message_queue` and `B210_Application`.

## Verdict

**(c) NO ATTRIBUTION.** The family remains proprietary/blocked (`investigate_before_implementing`).
Best supported origin: the B210/Bravechip "ChipletRing" platform middleware, authored as one
framework together with the generic device registry, RTC-device, time/calendar, and
sensor-stream families (shared 0..12 status enum, runtime vtable installation,
`i2c_n`/`sys rtc` naming). No open-source upstream tested (RT-Thread, Nordic, Linux, Zephyr,
vendor SDKs) matches at the function-behavior, constants, or structure level; there is no
"compatible-interval" candidate. The existing clean-room routing decision (Nordic TWIM/TWI
providers, or a separately attributable licensed soft-I2C provider) stands unchanged.
