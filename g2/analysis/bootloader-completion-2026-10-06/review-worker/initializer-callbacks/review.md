# Initializer callback review

`comparison.json` is a fresh PASS against locked image
`f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5`: 31
original/source comparisons, 60 direct mode-register cases, and 1,982 distinct
traced original instruction bytes. Current source ELF SHA256:
`11a5168432859aa550cfc1fad427eb855daa9853d777fd607fe15667ed2d5a3b`.

The profile executes stock callback entries `0x4301d6`, `0x43194c`, and
`0x415590`, with compiled source implementations for their wrappers and the
exercised nested bodies. Source owns mode-register helper `0x41d9aa`, the
four-row dispatcher `0x41f612`, ADC bringup `0x430000`, and eight-row finish
routine `0x430502`. The clock-manager implementation of power-register update
`0x41d92c` is linked into the source ELF and runs at all exercised call sites.
Service initialization/finalization and their exercised state helpers also
run from source. Tests compare ordered API calls, return status, service state,
row initialization bytes, context handles, semaphore store, ADC result bytes,
register-window writes, PRIMASK, and relevant arguments.

Mode-register cases exercise selectors 0–7, six IDs including byte wrapping
and bit 31, and both initial PRIMASK values for toggle selectors 2 and 5. The
MMIO register window is simulated. Post-bringup tests cover an empty table,
each row index, the special index-2 register path, and accumulated status.
Platform-finish tests cover empty/configured rows, existing/new context
handles, mutex failure, actual register validation failure for ID `0xe0`,
context-enable status, and semaphore failure. ADC cases supply a ready value
and three samples, including values below, between, and above thresholds, plus
continuation after context, transfer, profile, channel, and activation errors.

The ADC-ready register `0x40038038` and sample values are synthetic fixtures;
the profile makes no hardware timing or peripheral-behavior claim. Unicorn
cannot execute stock `VCVT.F64.F32`, `VSTR D0`, or `VMOV D0` instructions. The
test replaces only six fixed slots in its in-memory original mapping with
NOPs and emulates those specific register/store effects; the original bytes
remain recorded in the trace. Other stock instructions execute normally.

Named child providers remain at descriptor registration `0x430280`;
platform-finish HAL calls `0x42c4c6`, `0x42c988`, `0x42cc34`, `0x42c538`,
`0x43048e`, `0x42c63a`, `0x430470`, and `0x416762`; ADC APIs `0x42e8d0`,
`0x42ec0c`, `0x42f020`, `0x42eb74`, `0x42ea68`, `0x42eaf6`, `0x42ed60`,
`0x42ebaa`, `0x42eff4`, `0x42ee70`, `0x42ebe2`, `0x42eda0`, and `0x42ea32`;
post-bringup APIs `0x41f530`, `0x422ad4`, `0x422ba8`, `0x42308e`, `0x422dc6`,
`0x41f512`, `0x41f4f4`, `0x4236ce`, and `0x41f8ba`; service guard/commit/
wake/sleep; mutex creation; and logger.

The fixed-table runner separately tests its table entry and qsort; this
profile does not invoke all table rows end-to-end. The allocator has a separate
source profile. Physical hardware, scheduler delivery, logger formatting, full
startup, and byte identity remain outside this evidence.
