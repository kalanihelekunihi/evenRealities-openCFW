# Charger reset boundaries for wired recovery

The Smart Case's stock PB9 train and its selection of pogo charging/UART routes
are not proof of a physical Apollo reset. No pogo-to-PMIC-reset circuit has been
identified. The currently installed failed-update artifact and retail PMIC
register state are unknown. Do not turn a charger capability into a case command
without establishing that connection and observing the resulting reset class.

## Stock BQ25180 defaults: native execution

`build/wired-recovery-goal/check_native_charger_reset_policy.py` executes actual
2.2.6.10 `bq25180_apply_defaults` at `0x0053ADE6`, including its real setters and
read-modify-write logic. Only the I2C HAL is replaced with an explicit register
fixture. All 262 cases passed: zero seed, TI Rev C defaults, all 256 SHIP_RST
initial bytes, and four additional timer-field fixtures. No device is opened.
The result/provenance is `native-charger-reset-policy.json` beside the script;
a durable copy is in the adjacent webflasher's wired-recovery goal directory.

- No read or write of `SHIP_RST` (register 9) occurs in the traced initialization.
  Its initial value is preserved, rather than set to zero.
- `TMR_ILIM` retains its upper five bits and sets its low three bits to 6.
  The long-press timer, VIN qualifier and restart timer are not reconfigured.
- `IC_CTRL.WATCHDOG_SEL` becomes 0; that selection is register-default recovery,
  not the hardware-reset selections 1 or 2.
- `SYS_REG.SYS_MODE` becomes 0. This is ordinary power-path configuration.

The older zero-seeded model image ending `...44 06 00 21 00 F0` describes that
fixture only. With the TI default fixture, the native final image is
`00 00 00 5A 24 24 1F 44 4E 11 21 00 F0`. Neither is a retail register read.

[TI BQ25180 Rev C](https://www.ti.com/lit/ds/symlink/bq25180.pdf), sections 8.3.8,
8.5.1.8–10: TS/MR can request a configured long-press action. Reset register
`0x09=0x11` selects ship mode, not a hardware reset; timer `0x08=0x4D` selects
10 seconds. A hardware reset needs a different action or an I2C request.
These are component capabilities and fixture defaults, not measured glasses
configuration. No long pull or PMIC write was sent during this investigation.

## nPM1300 and board selection

The 2.2.6.10 board-ID code writes charger family 1 for all recognized ADC bins;
its `board_power_init_5093d4` selects nPM1300 for 1 and BQ25180/BQ27427 for 2.
This favors nPM1300 for that exact stock image. A physical family check and the
original pair's installed artifact are still needed; presence of both drivers
in a source tree is not a physical identification.

The [nPM1300 reset specification](https://docs.nordicsemi.com/r/bundle/ps_npm1300/page/chapters/core_components/reset/doc/frontpage.html)
describes SHPHLD and host-I2C reset routes. The pogo UART is not established as
that I2C bus or that pin. `npmx_main_driver.c` configures a PMIC watchdog;
`npmx_enter_ship_mode_512a70` requests ship mode and requires working application
code. Upstream `npmx_ship_task_trigger` task 3 requests reset *configuration*,
not the PMIC's separate TASKSWRESET. Do not substitute one for the other.

A useful next experiment needs one of: a responding application that exposes
identified PMIC state, measured access to the actual reset input, a known
pogo-reset decoder/circuit, or a non-destructive debugger read. Case-only UART
echo and software-model resets cannot establish these facts.
