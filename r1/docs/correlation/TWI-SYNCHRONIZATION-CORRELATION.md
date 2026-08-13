# TWI synchronization correlation

This closure admits fifteen small R1-owned register-transfer, synchronization, and lifecycle adapters around attributable Nordic and
CMSIS providers. It does not recreate a TWI driver, RTOS, semaphore, kernel-state query, tick
source, or delay primitive.

## Recovered functions

| Stock extent | Bytes | SHA-256 | Clean-room role |
|---|---:|---|---|
| `0x00054FF8..<0x00055058` | 96 | `c8acd79964fe902e645c7746a558e55c48193863ce1afd3ac589d89229230a64` | primary register read |
| `0x0005505C..<0x000550BA` | 94 | `85b332cad963abfdc137fb17b01ee74e1a49cdbe74fcae0b371b4c5a1c307ed0` | primary register write |
| `0x000550C0..<0x0005511A` | 90 | `1f2765c8851ddaeda3f395bd94de4d461671d3b76daf54ae3bce067a1b3fe0ca` | secondary register read |
| `0x00055120..<0x0005517A` | 90 | `92b75b75fcbc59ee64b0a6ae5730da7e3429c19c79f642ea158d3e5af5ea9f9b` | secondary register write |
| `0x00055180..<0x000551AC` | 44 | `ef7e71c634d021e67e566cf392fe76491ce05b6130dbf74d23bd21ef5277df47` | primary shutdown |
| `0x000551B4..<0x000551E0` | 44 | `0885b4df0a2992d0477849ac51e3a37b72591056048b84fcaf94a0e31eacc52a` | secondary shutdown |
| `0x000551E8..<0x00055206` | 30 | `8e917b01e58d21741dc590879c8ed6bc70635db30b3c0037dc42f916e512801b` | software `i2c_2` shutdown |
| `0x0005520C..<0x0005522A` | 30 | `8e917b01e58d21741dc590879c8ed6bc70635db30b3c0037dc42f916e512801b` | dormant software `i2c_3` shutdown |
| `0x00055230..<0x0005524E` | 30 | `8e917b01e58d21741dc590879c8ed6bc70635db30b3c0037dc42f916e512801b` | software `i2c_4` shutdown |
| `0x00055254..<0x00055272` | 30 | `8e917b01e58d21741dc590879c8ed6bc70635db30b3c0037dc42f916e512801b` | software `i2c_5` shutdown |
| `0x00055278..<0x000552DC` | 100 | `4516b8fdac0d5e34250cc0b59617c94e06a17faf0d15e6d9bf880deadd81b08d` | primary initialization/configuration |
| `0x000552E4..<0x00055326` | 66 | `9f391a5cad85e928b15715c8d0ead9bc34b40b4cd96797a96dbb4da73bc8c1fe` | secondary initialization/configuration |
| `0x00070778..<0x000707C6` | 78 | `ad1afebbb00454d0462173c6483d046232415ca58a07a27245e5ac8e3599a290` | transfer-completion adapter |
| `0x00070820..<0x00070884` | 100 | `e01f111c235bb727f1c37721cde083152dcf02e91c05f3ba4a16e5a2a1d6c30b` | primary wait adapter over state `0x20006FE8` |
| `0x0007088C..<0x000708F0` | 100 | `5109e14190c48c15212304581af701dea173926b74dcc682d42aa6ad5dc599be` | secondary wait adapter over state `0x20007054` |

The two wait functions have identical recovered behavior and differ only in their fixed state
object. OpenR1 consequently implements one typed `r1_twi_sync_wait` function and lets the caller
select the state. This is behavioral equivalence, not an attempt to preserve the stock compiler's
duplicate bodies or RAM layout.

## Lifecycle behavior

Both initializers return success without touching the provider when their state is already
initialized. The primary initializer first configures both caller-supplied pins with the recovered
numeric Nordic GPIO settings: output direction, disconnected input buffer, no pull, standard
`S0S1` drive, and no sense. The secondary initializer performs no explicit GPIO preconfiguration.
Both call Nordic `nrf_drv_twi_init` with 400 kHz frequency (`0x06680000`), interrupt priority 2,
`clear_bus_init=false`, the recovered event adapter, and the transfer-state context. The primary
configuration sets `hold_bus_uninit=true`; the secondary sets it false. A successful provider
initialization enables the underlying `nrfx_twim` instance and marks the local state initialized.

Stock passes a nonzero initialization result to its fatal-error path and then continues if that
path returns. OpenR1 deliberately fails closed instead: it returns the provider status, does not
enable the peripheral, and does not mark it initialized. This is a documented safety correction,
not a claim of byte-identical control flow.

Each primary/secondary shutdown is idempotent. When initialized it calls `nrfx_twim_disable`, then
`nrfx_twim_uninit`, writes zero and one to the peripheral `POWER` register at base plus `0xFFC`,
and clears the initialized flag. The recovered concrete register addresses are `0x40003FFC` and
`0x40004FFC`; the clean adapter derives the address from the Nordic instance rather than embedding
board globals.

The four software-bus shutdown wrappers are independently admitted from the initialized scatter
descriptors, not proximity. Their fixed states are `i2c_2` at `0x20007400`, dormant `i2c_3` at
`0x20007470`, `i2c_4` at `0x200074E0`, and `i2c_5` at `0x20007550`. Each checks its initialized
byte, invokes its offset-`0x30` callback first for the clock pin and then for the data pin, and
clears the byte. The four offset-`0x30` targets at `0x00078FE4`, `0x00078FF6`, `0x00079008`, and
`0x0007901A` are compiler-emitted Nordic `nrf_gpio_cfg_default` instances. OpenR1 therefore uses
that SDK helper directly and implements no bit-level software-I2C engine. The GPIO engines' open,
read, write, timing, and wire-level bodies remain outside this closure; `i2c_3` remains dormant and
unassigned.

## Register-transfer behavior

Both read adapters first transmit the one-byte register address with `no_stop=true`, wait, clear
only the completion byte, receive the payload, and wait again. The primary path clears both
completion and failure before the address phase, waits 500 ms for that phase, and truncates the
receive length to eight bits. The secondary path preserves the failure byte, waits 100 ms for the
address phase, and passes the full receive length to `nrfx_twim_rx`. Both data phases wait 200 ms
when the caller's original length is below 50, otherwise 500 ms.

Both write adapters reject payloads over 80 bytes with Nordic status `9`, build an 81-byte maximum
frame as register byte followed by payload, and transmit with `no_stop=false`. Nordic status `17`
(`NRF_ERROR_BUSY`) is returned immediately. Zero proceeds to the completion wait. Any other
immediate provider error is passed to the recovered fatal-error seam and the submission is retried
if that seam returns. The primary path clears failure and waits 500 ms; the secondary path
preserves failure and waits 200 ms. OpenR1 additionally rejects null caller/provider inputs rather
than dereferencing them.

## State and completion behavior

The relevant stock state bytes/word are represented as `completed`, `failed`,
`semaphore_enabled`, `semaphore`, and `status`. The completion adapter applies the recovered Nordic
event mapping:

- event `0` (`NRFX_TWIM_EVT_DONE`) sets `completed` and status `0`; it deliberately leaves the
  previous `failed` value unchanged;
- event `1` (`NRFX_TWIM_EVT_ADDRESS_NACK`) sets `completed`, `failed`, and status `5`;
- event `2` (`NRFX_TWIM_EVT_DATA_NACK`) sets `completed`, `failed`, and status `7`;
- any other event sets `completed` and `failed` but deliberately preserves the previous status.

If semaphore use is enabled, the handle is non-null, and `osKernelGetState()` returns exactly `2`
or `3`, the adapter calls `osSemaphoreRelease()`. Other kernel states do not release it.

## Wait behavior

When the same semaphore and kernel-state gate is true, the stock code computes unsigned
`(timeout_ms * osKernelGetTickFreq()) / 1000`, raises a zero result to one tick, and calls
`osSemaphoreAcquire()`. A nonzero CMSIS result maps to status `13`; success returns the state status.

Otherwise it polls `completed`. Before each delay it returns status `13` when
`timeout_ms * 1000 <= iteration`; otherwise it invokes Nordic `nrfx_coredep_delay_us(64)` and
increments the iteration. This means the stock polling ceiling is measured as 1,000 iterations per
requested millisecond while each iteration delays 64 microseconds. OpenR1 preserves that recovered
oddity for compatibility rather than silently treating the loop as a millisecond timer. The
unsigned multiplication behavior is also preserved.

OpenR1 adds only an argument guard: null state or incomplete operation tables return the public
argument status instead of dereferencing invalid pointers. Tests pin successful completion, both
NACK mappings, unknown-event retention, kernel states 2/3, tick conversion and one-tick minimum,
semaphore failure, polling completion, zero-timeout polling, and the 64-microsecond provider call.

## Provider boundary

The function-local callees identify the provider split:

- `0x0007D26C` — authenticated CMSIS-FreeRTOS `osKernelGetState`;
- `0x0007D2A4` — authenticated CMSIS-FreeRTOS `osKernelGetTickFreq`;
- `0x0007D57C` — authenticated CMSIS-FreeRTOS `osSemaphoreAcquire`;
- `0x0007D698` — authenticated CMSIS-FreeRTOS `osSemaphoreRelease`;
- `0x0009A5F0` and `0x0009A610` — Nordic `nrfx_coredep_delay_us` emitted machine-code helpers;
- the transaction callers use Nordic `nrf_drv_twi_tx` / `nrfx_twim_rx` providers.
- lifecycle calls resolve to Nordic `nrf_gpio_cfg`, `nrf_drv_twi_init`,
  `nrfx_twim_enable`, `nrfx_twim_disable`, and `nrfx_twim_uninit`.

The shared transfer core is also Nordic `nrfx_twim_xfer`. Ghidra represented it as one
690-byte non-contiguous function: a 32-byte entry veneer at `0x0007B448..<0x0007B468` and the
658-byte transfer body at `0x00093B34..<0x00093DC6`. Their ordered executable-byte SHA-256 is
`ca9b6b6b52c1b6dd2b4d481f79c68223e524ff55989efc77c5254cff187b07ab`. Its descriptor validation,
busy flag, EasyDMA setup, repeated-transfer flags, interrupt/event configuration, and blocking
completion/error paths match `modules/nrfx/drivers/src/nrfx_twim.c`; it is compiled from Nordic
source and is not locally recreated.

The ownership ledger classifies the eleven hardware-transfer/synchronization/lifecycle wrappers as
`r1_nordic_cmsis_provider_adapter` with disposition
`clean_room_adapter_only_use_nordic_sdk_and_cmsis`, and the four software-bus shutdown wrappers as
`r1_nordic_sdk_provider_adapter` with disposition `clean_room_adapter_only_use_nordic_sdk`. The
four transfer wrappers were admitted from
their own complete bodies and call boundaries, not by proximity to the wait functions. Nordic
TWI/TWIM lifecycle and transfer bodies, CMSIS synchronization, GPIO register helpers, and the SDK
fatal-error mechanism remain providers.

## Reproducible linked image

The nRF52840 target compiles the portable adapter with Nordic SDK 17.1.0 and the authenticated
CMSIS-FreeRTOS snapshot. The provider binding calls the upstream APIs directly and is retained by
`.openr1_twi_sync_api` at `0x0003B38C`, size `0x3C`.

- `r1_twi_sync_complete`: `0x00034652`, 88 bytes, SHA-256
  `f7bdf9580fcde91d729f133534e4f651591975ed2760bb3315eb7cf086672bd2`;
- `r1_twi_sync_wait`: `0x000346AA`, 120 bytes, SHA-256
  `584b34e54c3a986825fa84a9c0e97336d8d8e77780cd2572b6f534e6965f12e3`;
- primary read/write entry points: `0x0003485E` / `0x00034882`;
- secondary read/write entry points: `0x000348A6` / `0x000348C8`;
- generic lifecycle initialization: `0x000348EA`, 88 bytes, SHA-256
  `2cbb5c7e64dda235454c481c601b01e949109e97898b5f7818065aa511055e09`;
- primary/secondary initialization wrappers: `0x00034944` (36 bytes, SHA-256
  `1fd62cc12cdb1b3ead4285d22737bcc7ed53ae11bde6ac1ee5370c95b88c18e4`) and
  `0x00034968` (30 bytes, SHA-256
  `f7a1cc591451cdd5b1c728fe4385fa146d70aab9ed78a20a6d9e60ecc6915dd5`);
- lifecycle shutdown: `0x00034986`, 62 bytes, SHA-256
  `1cd1d451b9d88112e0729b00e81b856fa21138236ae1d2f9e269e951b0d58ec9`;
- software-bus shutdown: `0x000349C4`, 44 bytes, SHA-256
  `4253ee3285a206c22c23d5b5cbe9762e2a78b7f26374cd29725c58cf00fb1fd4`;
- provider operation tables: hardware lifecycle `0x0003AEE8` (28 bytes), software lifecycle
  `0x0003AF04` (8 bytes), sync `0x0003AF0C` (24 bytes), and transfer `0x0003AF24`
  (20 bytes).

The unsigned application image has text 90,956 bytes, data 236 bytes, and BSS 132,456 bytes. Its
HEX SHA-256 is `0954a9375874ee4f88139ba6243e20e1afba122e67afccba9d410e638053fa81`
and its BIN SHA-256 is
`31f3a97de9805239b03c51297f1de2ea9eaeff6fee372f1ea1f0c0a5c2f7bc91`.
No signing, verifier modification, or protection bypass is part of this closure.
