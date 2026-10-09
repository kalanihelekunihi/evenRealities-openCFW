# Codec UART lifecycle through recovered HAL power/configuration

**245 original/source compositions PASS** through reconstructed lifecycle,
actual recovered HAL UART power/configuration source, and prior ring/drain
source. [Cases and phase state](results.json), [final ELF and source hashes](reproduction-receipt.json),
[lifecycle source](../../components/audio/codec_uart_lifecycle_offline/lifecycle.c).

The original side executes stock lifecycle and HAL bodies. The native side
redirects stock HAL entries to compiled `am_hal_uart_power_control` and
`am_hal_uart_configure`; all other reached native instructions are guarded to
the final ELF. Peripheral-domain, clock, and GPIO calls remain explicit fixture
boundaries. Their arguments and ordered calls match; no physical state is
inferred from their supplied returns.

The composition confirms the earlier retained-RX result through the HAL path:
first initialize installs the callback and resets the 64-byte ring; close and
reopen do not reset it. An explicitly invoked RX callback writes `10 20 30`,
and the reopened reader drains the same three bytes. Callback invocation is a
software fixture, not simulated IRQ delivery or evidence that bytes arrive
while hardware is closed.

Provider failures need precise treatment. The recovered HAL power body ignores
the return values of peripheral enable/disable and clock request/release in the
tested normal/deep paths. Injected status7 at those boundaries therefore still
leads to lifecycle success and cannot support a physical failure claim.

The failed-close flag mismatch is reachable through the supported invalid-handle
path. Close clears channel active byte `descriptor+24` before HAL validation.
HAL returns invalid-handle status2, the channel wrapper returns1, and codec close
returns `-1` without clearing codec-open byte `0x20075015`. A subsequent host
initialize sees codec-open still1, skips channel enable, attempts baud on the
inactive/invalid descriptor, ignores that baud failure, and returns0. Software
state is then `initialized=1`, `open=1`, `active=0`. This is a proven software
fixture, not evidence that real hardware entered any particular power state.

Configuration reaches the recovered baud/clock/register body. Host init requests
115200 and still ignores its return. Synthetic revision/register backing and
provider responses do not establish measured baud, pin voltage, peripheral
readiness, quiescence, or transmitted data. Invalid-handle, initialized/open
0/1, sequential close/reopen/read, provider status0/7, channel narrowing, active
0/1/2, and callback/ring cases are covered.

Remaining source-ledger boundaries include GPIO frontend source, real interrupt
registration/delivery, complete initialized task/peripheral state, and physical
codec response ordering. Those require additional code or external traces;
this batch does not turn missing hardware evidence into a source-completion or
patch-safety claim.
