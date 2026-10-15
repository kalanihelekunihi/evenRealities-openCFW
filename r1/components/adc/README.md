# Native named ADC records and adapters

Three 40-byte records and the driver-initialized byte now have typed C initial
configuration at stock `0x20006EF4`. The records name `vbat_adc`,
`vpmic_isns_adc`, and `vnfc_rect_adc`; their channel configs use the actual
pinned Nordic types and asserted short-enum layout. The nine-byte config is
at +6 and the registry record is at +16. Initial state matches all 124 bytes
from authenticated scatter execution after name relocation.

Four native bodies compile: registration `0x5493C`, open `0x54864`, sample
`0x548F0`, close `0x547F4`. Registration clears the global initialized flag.
Open uses 12-bit resolution, priority 6, no oversampling/low-power mode and a
NULL event handler; channel index is the record index. It copies the stored
input selector into pin_p before channel setup, marks opened before reporting
a channel-init error, and requests two 64,000-cycle settling work units.

Close passes the stored input selector (6/4/3), unlike open's index (0/1/2).
This is observed stock behavior, not a claim of correct channel ownership.
It clears the record flag, scans all three records and uninitializes only
when all are closed and the initialized flag's low bit is set. Sample ignores
the provider status and copies its 16-bit result to the caller.

```
make -C r1 named-adc-candidate
make -C r1 named-adc-oracle PYTHON=/tmp/r1-source-venv/bin/python
```

All 354 bounded comparisons pass, including unknown names, flag states,
configuration bytes, provider-error callbacks, signed sample bit patterns and
all-channel close masks. Final nrfx/error seams are intercepted. Injected sample
providers always write the output, including on error; behavior when a failed
provider leaves an uninitialized local untouched remains unresolved. Settling
work is implemented through the recovered C busy-delay wrapper, whose exact
cycle timing remains unproven. Newlib strcmp is a binary test dependency.
Actual SAADC integration/conversions, fatal-error behavior, physical analog
measurements and complete application linking remain open.

The component now relocatably links the actual pinned `nrfx_saadc.c` object
(`adc/integration-report.json`). `verify_adc_sdk_execution.py` additionally
executes successful init/channel-init/channel-uninit/uninit paths without
provider interception. Ten calls match original Thumb on return values,
53 ordered peripheral/core writes and the 48-byte control block. The last
close exercises the bounded STOP-event timeout with the event unset; no
conversion result or asynchronous interrupt is synthesized. The fatal-error
symbol is a test-only trap and is never reached; its production body remains
unresolved. Newlib strcmp is an attributable binary test dependency. This
supersedes the earlier integration gate for these lifecycle paths, not the
physical sampling or failed-output gates.
