# R1 EAT response and signal callbacks in C, 2026-11-11

`native_eat_tx_registry.c` now owns the 512-byte response buffer immediately
after the 36-byte EAT registry, matching stock RAM offsets `0x20015464` and
`0x20015488`. `r1_eat_respond_format` uses the source-owned `vsnprintf`, then
routes a positive reported length through enabled channels one and two when
mode is zero, or channel two alone when mode is two. It preserves the stock
behavior of passing the formatter's reported length even when the buffer
truncates the text. The actual manifest object passed 500 paired stock/C
cases in `build/r1-eat-response-20261111/compare.py`, covering mode bytes,
channel masks, null callbacks, and negative, zero, and truncated lengths.
The probe substitutes the formatter and TX providers, so it validates routing
and buffer placement, not full formatting or transport delivery.

`native_eat_signal_commands.c` replaces the four short callbacks for
`AT^DFU`, `AT^FASTADV`, `AT^SLOWADV`, and `AT^STOPADV`. They call the existing
source-owned protocol-service thread flag provider with stock masks `4`,
`0x100`, `0x400`, and `0x80`. The actual manifest object passed 400 paired
stock/C calls in `build/r1-eat-signals-20261111/compare.py`; the thread flag
provider was intercepted, so scheduler and radio effects remain unverified.

`native_eat_pmic_isns_command.c` replaces `AT^PMIC_ISNS` with a call to the
existing source-owned VPMIC ADC reader and the shared EAT formatter. The
format text and reading argument matched stock in 300 paired cases using the
actual manifest object at `build/r1-eat-pmic-isns-20261111/compare.py`.
The ADC and formatter were intercepted in this probe; physical current-sense
accuracy remains unverified.

`native_eat_battery_adc_command.c` replaces `AT^BAT_ADC`. It reads the
source-owned battery voltage, charge-state byte and battery configuration,
then sends the stock text through the EAT formatter. The actual manifest
object passed 300 paired stock/C provider-order and formatter-argument cases
at `build/r1-eat-battery-adc-20261111/compare.py`.

`native_eat_temp_command.c` replaces `AT^TEMP`. It asks the existing C
two-sensor reducer for its five-byte result, preserves the count and signed
temperatures, and reports their average in the stock text. The actual
manifest object passed 500 paired stock/C cases at
`build/r1-eat-temp-20261111/compare.py`, including negative sensor values;
the reducer and formatter were intercepted.

`native_eat_ble_log_command.c` replaces `AT^BLE_LOG`. It maps arguments
`0`, `1`, and `2` to mode bytes `1`, `2`, and `4`, and sends stock success or
error text. The existing `stock_seams.c` now owns the stock one-byte mode
setter. Their actual manifest objects passed 400 paired stock/C cases at
`build/r1-eat-ble-log-20261111/compare.py`; the formatter was intercepted.

`native_activity_accumulator.c` now also owns stock `0x491bc`, the
latest-eight-byte snapshot getter from its existing 24-byte state.
`native_eat_activity_read_command.c` uses that getter for
`AT^ACTIVITY_READ`. The actual manifest objects passed 900 paired stock/C
getter and command calls, including null output and randomized state, at
`build/r1-eat-activity-20261111/compare.py`. The probe caught and corrected
the response argument order before this receipt.

`native_eat_touch_hw_command.c` replaces `AT^TOUCH_HW` using the existing
source-owned hardware-variant and product-size providers. Its actual manifest
object passed 300 paired stock/C calls across variant values and ring sizes
at `build/r1-eat-touch-hw-20261111/compare.py`; the lower providers and
formatter were intercepted.

`native_eat_wear_status_command.c` replaces `AT^WEAR_STATUS`; 300 paired
stock/C cases matched the Boolean health-mode conversion and reply. The
provider and formatter were intercepted at
`build/r1-eat-wear-status-20261111/compare.py`.

`native_peripheral_watchdog.c` now also owns stock `0x4da1c` and the
keep-connected byte adjacent to its existing counter. The
`AT^BLE_KEEPCONNECT` callback sets that byte and sends the stock reply.
The actual manifest objects passed 800 paired stock/C setter and command
calls at `build/r1-eat-keep-connected-20261111/compare.py`.

`native_eat_pmic_read_command.c` replaces `AT^PMIC_READ` using the existing
source-owned nine-byte charger read. Its zero-initialized buffer supplies a
zero tenth displayed byte. The actual manifest object passed 400 paired
stock/C cases checking both response calls and all ten register arguments at
`build/r1-eat-pmic-read-20261111/compare.py`; the lower provider and
formatter were intercepted.

`native_dock_policy.c` now also owns the stock dock hardware and version
get/clear helpers at `0x77250..0x77289`, using its existing source-owned
state. `native_eat_charge_version_commands.c` consumes those values for
`AT^CHARGE_HW_VER` and `AT^CHARGE_VER`. Their actual manifest objects passed
1,800 paired stock/C getter, clear and command calls with randomized dock
bytes and version strings at `build/r1-eat-charge-ver-20261111/compare.py`.
The probe models the stock `__aeabi_memclr`, the source `memset`, `strlen`
and the response formatter; physical NFC exchange remains unverified.

`native_eat_sdver_command.c` reports the SoftDevice version through the
existing source-owned diagnostic logger. Its callback and logger passed 500
paired stock/C cases at `build/r1-eat-sdver-20261111/compare.py`.
`native_eat_dock_settings_commands.c` implements `AT^CHARGE_TEMP` and
`AT^DOCK_ADV_SET`, including the stock temperature-byte write on a rejected
parse. The callback and dock-state objects passed 800 paired cases at
`build/r1-eat-dock-settings-20261111/compare.py`.
`native_eat_touch_init_command.c` passed 400 paired command cases at
`build/r1-eat-touch-init-20261111/compare.py`; the lower touch-service
providers were intercepted.

`native_eat_fast_command.c` and the source-owned delayed fast connection
update passed 800 paired stock/C calls at
`build/r1-eat-fast-20261111/compare.py`. `native_eat_device_id_command.c`
passed 400 paired calls at `build/r1-eat-devid-20261111/compare.py` with
the sensor providers intercepted. `native_eat_log_command.c` and the
source-owned threshold setter passed 400 paired calls at
`build/r1-eat-log-20261111/compare.py`, including rejected mode values and
the state changes on those paths. `native_eat_info_command.c` and its BLE
name getter passed 400 paired calls at
`build/r1-eat-info-20261111/compare.py`, including failing address requests;
the SoftDevice supervisor call and formatter were modeled.

`native_eat_pmic_off_command.c` now performs the stock power-off persistence
request and worker signal. Its actual callback object passed 400 paired
stock/C calls at `build/r1-eat-pmic-off-20261111/compare.py`; the battery,
time, KV and scheduler providers were intercepted. The command is therefore
source-callable, but physical power-off behavior has not been tested.
`native_eat_kv_read_command.c` and the source-owned seven-record lookup
passed 400 paired callback cases plus 400 paired lookup cases at
`build/r1-eat-kv-read-20261111/compare.py` and
`compare_provider.py`. These probes model parsing, record contents and
formatting; they do not exercise flash storage.

`native_eat_stream_commands.c` adds the source-owned five-slot EAT stream
handle array and the five `*_CLOSE` callbacks. They conditionally unregister
the live `hr`, `spo2`, `temp`, `hrv`, or `acc` stream and clear its handle.
The actual manifest object passed 500 paired stock/C cases at
`build/r1-eat-stream-close-20261111/compare.py`, including a provider that
mutates the handle slot during the call. The matching five `*_OPEN` callbacks
register their stock stream names, `at` group, sample callback, order and
flags. Their actual manifest object passed 500 paired stock/C cases at
`build/r1-eat-stream-open-20261111/compare_open.py`, including provider
mutation of the handle slot.

`native_eat_stream_samples.c` supplies the five registered sample reporters.
The actual manifest object passed 500 paired stock/C cases at
`build/r1-eat-stream-open-20261111/compare_samples.py`, checking format text,
arguments and temperature sample mutation. The accelerometer cases cover
record counts through 15. All stream probes intercept registration,
unregistration or TX formatting providers; stream hardware and real transport
remain unverified.

`./make.sh sources-check` passes with 1,009 R1 units, 796 source files and zero
unbuilt units. The latest source composition compiles 927 application and 82
bootloader units with no duplicate strong symbols. The strict bootloader
link and C vector pass. The strict application link has 15 undefined
references, including `AT^RESET_RING` and 14 other functions;
it uses 637,048 of 696,320 flash bytes without overflow. Receipts:

- `build/sources-r1-eat-kv-read-c-20261111/report.json`
- `build/r1-link-eat-kv-read-c-20261111/report.json`
- `build/r1-boot-link-eat-kv-read-c-20261111/report.json`
- `build/sources-r1-eat-kv-read-all-stable-20261111/report.json` (all-tree
  build: every listed G2 and R1 payload compiled without failures or
  duplicate strong symbols)

Application link completion, removal of embedded assembly, whole-image byte
equality, and hardware execution remain unfinished.
