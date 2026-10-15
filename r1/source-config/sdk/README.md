# R1 application SDK candidate configuration

This is an additive application configuration, separate from the preserved
historical `config-recovered/sdk_config.h`. That seed mixes proven values and
historical choices; its confidence table remains applicable. Missing values
come from the unmodified SDK 17.1.0 `ble_app_hrs_freertos` example header,
generated locally as `r1_sdk_example_defaults.h`. Those defaults are explicitly
**not stock-proven**. The build authenticates the archive and the entire
extracted SDK tree before using it.

## Recovered overrides

| Override | Evidence |
|---|---|
| RTT down buffer 64 bytes | `correlation/NORDIC-SDK-CORRELATION.md:913-915`; the historical 16-byte value is documented as wrong for stock |
| Logging enabled/deferred and its memobj/balloc/ringbuf/fprintf chain | complete logger dequeue and standard wrappers, `NORDIC-SDK-CORRELATION.md:402-407` |
| QWR enabled with zero extra attributes | `NORDIC-SDK-CORRELATION.md:383-387` |
| Buttonless DFU enabled, unbonded path, SVCI BLE transport | `closures/NORDIC-BUTTONLESS-DFU-CLOSURE.md`; stock SVCI function 3 |
| Power management enabled, scheduler dispatch disabled | `closures/NORDIC-POWER-MANAGEMENT-CLOSURE.md` |
| TIMER2 and TIMER4 only | exact IRQ wrappers/control-block identities at `NORDIC-SDK-CORRELATION.md:684-685`; authenticated application vectors |
| NFCT and PDM driver bodies linked | `NORDIC-SDK-CORRELATION.md:539-549,921-926`; authenticated vectors |

The example's legacy RTC, SAADC, SPI, WDT, PDM and TIMER aliases would override
nrfx settings via `apply_old_config.h`. Conflicting namespaces are removed in
the R1-owned header so recovered nrfx selections survive. The TWI/clock legacy
adapters retain the aliases their upstream implementations require. Remaining
legacy/default values require separate recovery, not an assumption of equality.

The build checks effective selections after including `nrfx.h`. It verifies
eight vector words against the pinned application: RTC2, TIMER2, TIMER4, NFCT
and PDM point to their recovered handlers, while TIMER0/1/3 point to the shared
default handler. These checks support linked-code/configuration selections;
they do not prove that a peripheral is initialized or functional on hardware.

## Compiler adaptations

Clang formats GCC inline-assembly constant operands with a leading `#`, which
makes the SDK's `ldr ..., =%N` literal syntax invalid. The candidate build
applies only `%4 -> %c4` in `app_error_handler_gcc.c` and `%0 -> %c0` in the two
SVCI literal loads. Reviewable patches live in `r1/patches/nrf5-sdk/`; generated
copies retain the SDK notices and the authenticated SDK tree stays unmodified.
The SVCI header is pre-included to retain its original guard across quoted
includes. The compiled advertisement-name SVCI stub is checked to load R12=3,
execute SVC 0 and return. It is not replaced by a normal function call.

These adaptations make a Clang diagnostic build possible; stock ArmCC startup,
error handling, register allocation and placement remain unresolved. The GNU
error-handler unit is a candidate, not proof of the stock ArmCC implementation.
All unspecified logger sizing, driver options, priorities and example defaults
remain configuration gates even when all translation units compile.

## GPIOTE low-power slots (2026-10-15)

The historical seed's two low-power events was contradicted by original
`nrfx_gpiote_init` at `0x7A94C`: it initializes 16 handlers and uses pin
assignments +64, configured pins +120 and state +126. With eight hardware
channels the original layout is eight low-power slots, 128 bytes total.
The R1 configuration now sets `NRFX_GPIOTE_CONFIG_NUM_OF_LOW_POWER_EVENTS=8`
and removes `GPIOTE_ENABLED` from the SDK example legacy namespace so
`apply_old_config.h` cannot overwrite this proven value. The effective
configuration probe asserts eight. Six additional assertions against the actual
SDK-private control-block type establish the stock field offsets and extent.
Other GPIOTE options, logging variations, physical IRQ behavior and original
instruction identity remain independently gated.

## GPIOTE IRQ priority (2026-10-15)

Original nrfx init writes `0xC0` to the IRQ6 priority byte, while the historical
priority 2 produced `0x40`. The stock-versus-compiled executable differential
caught this mismatch. Source-owned priority is now 6, with an effective compile
time assertion. After rebuilding all SDK consumers, 29 lifecycle calls agree
on statuses, ordered peripheral/core writes and normalized control state.
The test uses Cortex-M execution mode so stock IPSR/BASEPRI instructions in
logging paths execute, rather than intercepting provider functions. It does
not establish asynchronous IRQ delivery or hardware timing.
